const std = @import("std");
const builtin = @import("builtin");
const py = @import("py");
const zodbc = @import("zodbc");
const utils = @import("utils.zig");
const PyFuncs = @import("PyFuncs.zig");
const FetchPy = @import("fetch_py.zig");
const put_py = @import("put_py.zig");
const fetch_py = FetchPy.fetch_py;
const FetchArrow = @import("fetch_arrow.zig");
const put_arrow = @import("put_arrow.zig");
const put_common = @import("put_common.zig");
const arrow = @import("arrow.zig");
const c = py.py;
const Obj = *c.PyObject;

const PyErr = py.PyErr;

const DebugAllocator = std.heap.DebugAllocator(.{
    .never_unmap = true,
    .retain_metadata = true,
    .safety = true,
    .thread_safe = true,
});

const EnvCon = struct {
    env: zodbc.Environment,
    con: zodbc.Connection,
    py_funcs: PyFuncs,
    closed: bool = false,
    dbg_allocator: if (builtin.mode == .Debug) *DebugAllocator else void,
    ally: std.mem.Allocator,

    fn close(self: *EnvCon) !void {
        if (self.closed) return;
        self.closed = true;
        self.con.endTran(.rollback) catch return self.con.getLastError();
        self.con.disconnect() catch return self.con.getLastError();
    }

    /// Only called via garbage collection
    fn deinit(self: *EnvCon) callconv(.c) void {
        self.close() catch {};
        self.py_funcs.deinit();
        // TODO maybe use python warnings?
        self.con.deinit() catch {};
        self.env.deinit() catch {};
        if (builtin.mode == .Debug) {
            if (self.dbg_allocator.deinit() != .ok) @panic("Memory issue");
            std.heap.c_allocator.destroy(self.dbg_allocator);
        }
    }
};
const ConnectionCapsule = py.PyCapsule(EnvCon, "zodbc_con", EnvCon.deinit);

const Stmt = struct {
    stmt: zodbc.Statement,
    /// Keep a reference to the connection capsule so it isn't
    /// accidentally garbage collected before all its statements
    env_con_caps: Obj,
    /// Borrowed reference
    env_con: *const EnvCon,
    dt7_fetch: utils.Dt7Fetch,
    rowcount: i64 = -1,

    result_set: ?struct {
        result_set: zodbc.ResultSet,
        stmt: *const Stmt,
        cache_column_names: ?std.ArrayListUnmanaged([:0]const u8) = null,
        cache_tuple_type: ?*c.PyTypeObject = null,
        cache_fetch_py_state: ?FetchPy = null,
        cache_fetch_arrow_state: ?FetchArrow = null,

        fn init(stmt: *const Stmt, allocator: std.mem.Allocator) !@This() {
            var thread_state = c.PyEval_SaveThread();
            defer if (thread_state) |t_state| c.PyEval_RestoreThread(t_state);
            const desc = try zodbc.Descriptor.AppRowDesc.fromStatement(stmt.stmt);
            const result_set = zodbc.ResultSet.init(
                stmt.stmt,
                desc,
                allocator,
            ) catch |err| switch (err) {
                error.NumResultColsError,
                error.NumResultColsSuccessWithInfo,
                error.NumResultColsInvalidHandle,
                => |err_i| return utils.odbcErrToPy(stmt.stmt, "NumResultCols", err_i, &thread_state),

                error.ColAttributeError,
                error.ColAttributeSuccessWithInfo,
                error.ColAttributeInvalidHandle,
                error.ColAttributeNoData,
                => |err_i| return utils.odbcErrToPy(stmt.stmt, "ColAttribute", err_i, &thread_state),

                error.BindColError,
                error.BindColSuccessWithInfo,
                error.BindColInvalidHandle,
                => |err_i| return utils.odbcErrToPy(stmt.stmt, "BindCol", err_i, &thread_state),

                error.SetStmtAttrError,
                error.SetStmtAttrSuccessWithInfo,
                error.SetStmtAttrInvalidHandle,
                => |err_i| return utils.odbcErrToPy(stmt.stmt, "SetStmtAttr", err_i, &thread_state),

                error.SetDescFieldError,
                error.SetDescFieldSuccessWithInfo,
                error.SetDescFieldInvalidHandle,
                error.OutOfMemory,
                => |err_i| return utils.odbcErrToPy(desc, "SetDescField", err_i, &thread_state),

                error.NoResultSet => return error.@"No results",
                inline else => |err_i| {
                    if (comptime std.mem.startsWith(u8, @errorName(err_i), "Unsupported SQL Type: ")) {
                        return err;
                    }
                    @compileError("Need to implement error handling for " ++ @errorName(err_i));
                },
            };
            return .{
                .result_set = result_set,
                .stmt = stmt,
            };
        }

        fn deinit(self: *@This()) !void {
            if (self.cache_column_names) |*names| {
                for (names.items) |name| {
                    self.stmt.env_con.ally.free(name);
                }
                names.deinit(self.stmt.env_con.ally);
            }
            if (self.cache_tuple_type) |tp| {
                c.Py_DECREF(@ptrCast(@alignCast(tp)));
            }
            if (self.cache_fetch_py_state) |fp| {
                fp.deinit(self.stmt.env_con.ally);
            }
            if (self.cache_fetch_arrow_state) |fa| {
                fa.deinit(self.stmt.env_con.ally);
            }
            try self.result_set.deinit();
        }

        pub fn columnNames(self: *@This()) ![][:0]const u8 {
            if (self.cache_column_names) |names| {
                return names.items;
            }

            const n_cols = self.result_set.n_cols;
            var names = try std.ArrayListUnmanaged([:0]const u8).initCapacity(
                self.stmt.env_con.ally,
                n_cols,
            );
            errdefer names.deinit(self.stmt.env_con.ally);
            errdefer for (names.items) |name| self.stmt.env_con.ally.free(name);

            for (0..n_cols) |i_col| {
                const col_name = try self.result_set.stmt.colAttributeString(
                    @intCast(i_col + 1),
                    .name,
                    self.stmt.env_con.ally,
                );
                errdefer self.stmt.env_con.ally.free(col_name);
                names.appendAssumeCapacity(col_name);
            }
            self.cache_column_names = names;
            return names.items;
        }

        pub fn tupleType(self: *@This()) !*c.PyTypeObject {
            if (self.cache_tuple_type) |tp| {
                return tp;
            }
            const names = try self.columnNames();
            const fields = try self.stmt.env_con.ally.alloc(c.PyStructSequence_Field, names.len + 1);
            defer self.stmt.env_con.ally.free(fields);
            fields[fields.len - 1] = c.PyStructSequence_Field{ .doc = null, .name = null };
            for (names, 0..) |name, i_name| {
                fields[i_name] = .{
                    .doc = null,
                    .name = name.ptr,
                };
            }

            var desc: c.PyStructSequence_Desc = .{
                .doc = "Rows from a zodbc query",
                .n_in_sequence = @intCast(fields.len - 1),
                .name = "zodbc.Row",
                .fields = fields.ptr,
            };
            const tp = c.PyStructSequence_NewType(&desc) orelse return PyErr;
            self.cache_tuple_type = tp;
            return tp;
        }

        pub fn fetchPyState(self: *@This()) !FetchPy {
            if (self.cache_fetch_py_state) |fp| {
                return fp;
            }
            const fp = try FetchPy.init(
                &self.result_set,
                self.stmt.env_con.ally,
                self.stmt.dt7_fetch,
            );
            self.cache_fetch_py_state = fp;
            return fp;
        }

        pub fn fetchArrowState(self: *@This()) !FetchArrow {
            // TODO error when switching between fetch py/arrow?
            if (self.cache_fetch_arrow_state) |fa| {
                return fa;
            }
            const fa = try FetchArrow.init(
                &self.result_set,
                self.stmt.env_con.ally,
                self.stmt.dt7_fetch,
            );
            self.cache_fetch_arrow_state = fa;
            return fa;
        }
    } = null,

    fn deinit(self: *Stmt) callconv(.c) void {
        deinit_err(self) catch {};
    }

    fn deinit_err(self: *Stmt) !void {
        if (self.result_set) |*result_set| {
            try result_set.deinit();
            self.result_set = null;
        }
        try self.stmt.deinit();
        c.Py_DECREF(self.env_con_caps);
    }
};
const StmtCapsule = py.PyCapsule(Stmt, "zodbc_stmt", Stmt.deinit);

pub fn connect(constr: []const u8, autocommit: bool) !Obj {
    const env = try zodbc.Environment.init(.v3_80);
    errdefer env.deinit() catch {};
    const con = try zodbc.Connection.init(env);
    errdefer con.deinit() catch {};
    // on by default
    if (!autocommit)
        try con.setConnectAttr(.{ .autocommit = .off });
    try con.connectWithString(constr);
    errdefer con.disconnect() catch {};

    const py_funcs = try PyFuncs.init();
    errdefer py_funcs.deinit();

    const dbg, const ally = if (builtin.mode == .Debug) blk: {
        const dbg = std.heap.c_allocator.create(DebugAllocator) catch unreachable;
        dbg.* = .init;
        dbg.backing_allocator = std.heap.c_allocator;
        break :blk .{ dbg, dbg.allocator() };
    } else .{ void{}, std.heap.c_allocator };

    return try ConnectionCapsule.create_capsule(EnvCon{
        .env = env,
        .con = con,
        .py_funcs = py_funcs,
        .dbg_allocator = dbg,
        .ally = ally,
    });
}

pub fn setAutocommit(con: Obj, autocommit: bool) !void {
    const env_con = try ConnectionCapsule.read_capsule(con);
    try env_con.con.setConnectAttr(.{ .autocommit = if (autocommit) .on else .off });
}

pub fn getAutocommit(con: Obj) !bool {
    const env_con = try ConnectionCapsule.read_capsule(con);
    var odbc_buf: [1024]u8 = undefined;
    odbc_buf = std.mem.zeroes(@TypeOf(odbc_buf));
    const autocommit = try env_con.con.getConnectAttr(
        env_con.ally,
        .autocommit,
        odbc_buf[0..],
    );
    return switch (autocommit.autocommit) {
        .on => true,
        .off => false,
    };
}

pub fn cursor(con: Obj, datetime2_7_fetch: utils.Dt7Fetch) !Obj {
    const env_con = try ConnectionCapsule.read_capsule(con);
    const stmt = try zodbc.Statement.init(env_con.con);
    errdefer stmt.deinit() catch {};
    return try StmtCapsule.create_capsule(.{
        .stmt = stmt,
        .env_con_caps = c.Py_NewRef(con),
        .env_con = env_con,
        .dt7_fetch = datetime2_7_fetch,
    });
}

pub fn execute(cur_obj: Obj, query: []const u8, py_params: Obj) !void {
    const cur = try StmtCapsule.read_capsule(cur_obj);
    if (cur.result_set) |*result_set| {
        try result_set.deinit();
        // try cur.stmt.closeCursor();
        cur.result_set = null;
    }
    // Fixes issue with multiple execute calls without fetches but can error.
    // Maybe better to discard individual result sets?
    cur.stmt.closeCursor() catch {};

    var prepared = false;

    var params = try put_py.bindParams(
        cur.stmt,
        py_params,
        cur.env_con.ally,
        cur.env_con.py_funcs,
        &prepared,
        query,
    );
    defer put_common.deinitParams(&params, cur.env_con.ally);
    errdefer if (params.items.len > 0) cur.stmt.free(.reset_params) catch {};

    var thread_state = c.PyEval_SaveThread();
    defer if (thread_state) |t_state| c.PyEval_RestoreThread(t_state);
    if (prepared) {
        cur.stmt.execute() catch |err| switch (err) {
            error.ExecuteNoData => {},
            error.ExecuteSuccessWithInfo => {},
            else => return utils.odbcErrToPy(cur.stmt, "Execute", err, &thread_state),
        };
    } else {
        cur.stmt.execDirect(query) catch |err| switch (err) {
            error.ExecDirectNoData => {},
            error.ExecDirectSuccessWithInfo => {},
            else => return utils.odbcErrToPy(cur.stmt, "ExecDirect", err, &thread_state),
        };
    }

    try put_common.checkTooManyParams(cur.stmt, params.items.len, &thread_state);

    cur.rowcount = cur.stmt.rowCount() catch |err|
        return utils.odbcErrToPy(cur.stmt, "RowCount", err, &thread_state);

    if (params.items.len > 0) cur.stmt.free(.reset_params) catch |err|
        return utils.odbcErrToPy(cur.stmt, "FreeStmt", err, &thread_state);
}

pub fn fetchmany(cur_obj: Obj, n_rows: ?usize) !Obj {
    const cur = try StmtCapsule.read_capsule(cur_obj);
    if (cur.result_set == null) {
        cur.result_set = try .init(cur, cur.env_con.ally);
    }
    return fetch_py(
        &try cur.result_set.?.fetchPyState(),
        &cur.result_set.?.result_set,
        cur.env_con.ally,
        n_rows,
        &cur.env_con.py_funcs,
        .tuple,
        void{},
        void{},
    );
}

pub fn fetchdicts(cur_obj: Obj, n_rows: ?usize) !Obj {
    const cur = try StmtCapsule.read_capsule(cur_obj);
    if (cur.result_set == null) {
        cur.result_set = try .init(cur, cur.env_con.ally);
    }

    const names = try cur.result_set.?.columnNames();
    for (names[0 .. names.len - 1], 0..) |name, i_name| {
        for (names[i_name + 1 ..], 0..) |name2, i_name2| {
            if (std.mem.eql(u8, name, name2)) {
                return py.raise(
                    .ValueError,
                    "Column name '{s}' appears twice at positions {} and {}",
                    .{ name, i_name, i_name2 },
                );
            }
        }
    }

    return fetch_py(
        &try cur.result_set.?.fetchPyState(),
        &cur.result_set.?.result_set,
        cur.env_con.ally,
        n_rows,
        &cur.env_con.py_funcs,
        .dict,
        names,
        void{},
    );
}

pub fn fetchnamed(cur_obj: Obj, n_rows: ?usize) !Obj {
    const cur = try StmtCapsule.read_capsule(cur_obj);
    if (cur.result_set == null) {
        cur.result_set = try .init(cur, cur.env_con.ally);
    }
    return fetch_py(
        &try cur.result_set.?.fetchPyState(),
        &cur.result_set.?.result_set,
        cur.env_con.ally,
        n_rows,
        &cur.env_con.py_funcs,
        .named,
        void{},
        try cur.result_set.?.tupleType(),
    );
}

pub fn exp_put(val: Obj, con: Obj) ![]const u8 {
    const env_con = try ConnectionCapsule.read_capsule(con);
    return @tagName(try @import("put_py.zig").Conv.fromValue(val, env_con.py_funcs));
}

pub fn getinfo(con: Obj, info_name: []const u8) !Obj {
    const env_con = try ConnectionCapsule.read_capsule(con);
    if (std.meta.stringToEnum(zodbc.odbc.info.InfoTypeString, info_name)) |tag| {
        const info = env_con.con.getInfoString(
            env_con.ally,
            tag,
        ) catch |err| return utils.odbcErrToPy(env_con.con, "GetInfo", err, null);
        defer env_con.ally.free(info);
        // ld.so assertion trips in debug mode without inlining, maybe zig bug? TODO try again in 0.16
        return @call(.always_inline, py.zig_to_py, .{info});
    }
    if (std.meta.stringToEnum(zodbc.odbc.info.InfoType, info_name)) |tag| {
        switch (tag) {
            inline else => |tag_comp| {
                const info = env_con.con.getInfoComptime(
                    tag_comp,
                ) catch |err| return utils.odbcErrToPy(env_con.con, "GetInfo", err, null);
                if (@typeInfo(@TypeOf(info)) == .@"enum") {
                    return py.zig_to_py(@tagName(info));
                } else {
                    return py.zig_to_py(info);
                }
            },
        }
    }

    const msg = comptime blk: {
        const fields = @typeInfo(zodbc.odbc.info.InfoTypeString).@"enum".fields ++ @typeInfo(zodbc.odbc.info.InfoType).@"enum".fields;
        var len = 0;
        for (fields) |field| {
            len += field.name.len + 2; // 2 for the quotes
        }
        len -= 2; // remove the last comma
        var opts: [len]u8 = undefined;
        var ix = 0;
        for (fields, 0..) |field, i_field| {
            @memcpy(opts[ix..].ptr, field.name);
            ix += field.name.len;
            if (i_field < fields.len - 1) {
                @memcpy(opts[ix..].ptr, ", ");
                ix += 2;
            }
        }
        std.debug.assert(ix == opts.len);
        break :blk "Unknown option {s}. Available: " ++ opts;
    };
    return py.raise(.ValueError, msg, .{info_name});
}

pub fn commit(con: Obj) !void {
    const env_con = try ConnectionCapsule.read_capsule(con);
    const thread_state = c.PyEval_SaveThread();
    defer c.PyEval_RestoreThread(thread_state);
    try env_con.con.endTran(.commit);
}

pub fn rollback(con: Obj) !void {
    const env_con = try ConnectionCapsule.read_capsule(con);
    const thread_state = c.PyEval_SaveThread();
    defer c.PyEval_RestoreThread(thread_state);
    try env_con.con.endTran(.rollback);
}

pub fn nextset(cur_obj: Obj) !bool {
    const cur = try StmtCapsule.read_capsule(cur_obj);
    if (cur.result_set) |*result_set| {
        try result_set.deinit();
        cur.result_set = null;
    }
    var thread_state = c.PyEval_SaveThread();
    defer if (thread_state) |t_state| c.PyEval_RestoreThread(t_state);
    cur.stmt.moreResults() catch |err| switch (err) {
        error.MoreResultsNoData => return false,
        else => return utils.odbcErrToPy(cur.stmt, "MoreResults", err, &thread_state),
    };
    cur.rowcount = cur.stmt.rowCount() catch |err|
        return utils.odbcErrToPy(cur.stmt, "RowCount", err, &thread_state);

    return true;
}

pub fn con_close(con: Obj) !void {
    const env_con = try ConnectionCapsule.read_capsule(con);
    try env_con.close();
}

pub fn con_closed(con: Obj) !bool {
    const env_con = try ConnectionCapsule.read_capsule(con);
    return env_con.closed;
}

pub fn cur_deinit(cur: Obj) !void {
    const stmt = try StmtCapsule.read_capsule(cur);
    try stmt.deinit_err();
}

pub fn rowcount(cur_obj: Obj) !i64 {
    const cur = try StmtCapsule.read_capsule(cur_obj);
    return cur.rowcount;
}

pub fn cancel(cur_obj: Obj) !void {
    var thread_state = c.PyEval_SaveThread();
    defer if (thread_state) |t_state| c.PyEval_RestoreThread(t_state);
    const cur = try StmtCapsule.read_capsule(cur_obj);
    cur.stmt.cancel() catch |err| switch (err) {
        error.CancelSuccessWithInfo => {}, // happens sometimes with sql server and no info is provided
        else => return utils.odbcErrToPy(cur.stmt, "Cancel", err, &thread_state),
    };
}

pub fn arrow_batch(cur_obj: Obj, n_rows: usize) !struct { Obj, Obj } {
    const cur = try StmtCapsule.read_capsule(cur_obj);
    if (cur.result_set == null) {
        cur.result_set = try .init(cur, arrow.ally);
    }

    const fetch_arrow = try cur.result_set.?.fetchArrowState();

    const schema, const array = try fetch_arrow.fetch_batch(
        &cur.result_set.?.result_set,
        arrow.ally,
        n_rows,
    );

    return .{
        try arrow.SchemaCapsule.create_capsule(schema),
        try arrow.ArrayCapsule.create_capsule(array),
    };
}

pub fn executemany_arrow(cur_obj: Obj, query: []const u8, schema_caps: Obj, array_caps: Obj) !void {
    const schema_batch = try arrow.SchemaCapsule.read_capsule(schema_caps);
    const array_batch = try arrow.ArrayCapsule.read_capsule(array_caps);

    const cur = try StmtCapsule.read_capsule(cur_obj);
    if (cur.result_set) |*result_set| {
        try result_set.deinit();
        cur.result_set = null;
    }
    var thread_state = c.PyEval_SaveThread();
    defer if (thread_state) |t_state| c.PyEval_RestoreThread(t_state);
    // Fixes issue with multiple execute calls without fetches but can error.
    // Maybe better to discard individual result sets?
    cur.stmt.closeCursor() catch {};

    errdefer cur.stmt.free(.reset_params) catch {};
    put_arrow.executeMany(
        cur.stmt,
        query,
        schema_batch,
        array_batch,
        cur.env_con.ally,
        &thread_state,
    ) catch |err| switch (err) {
        error.PyErr => return PyErr,
        error.OutOfMemory => return utils.raise(.Exception, "Ran out of memory", .{}, &thread_state),
    };
    cur.stmt.free(.reset_params) catch |err|
        return utils.odbcErrToPy(cur.stmt, "FreeStmt", err, &thread_state);
}

pub fn close_cursor(cur_obj: Obj) !void {
    const cur = try StmtCapsule.read_capsule(cur_obj);
    if (cur.result_set) |*result_set| {
        try result_set.deinit();
        cur.result_set = null;
    }
    cur.stmt.closeCursor() catch |err|
        return utils.odbcErrToPy(cur.stmt, "CloseCursor", err, null);
}

pub fn column_names(cur_obj: Obj) !?[][:0]const u8 {
    const cur = try StmtCapsule.read_capsule(cur_obj);
    const RST = @typeInfo(@FieldType(Stmt, "result_set")).optional.child;
    if (cur.result_set == null) {
        cur.result_set = RST.init(cur, cur.env_con.ally) catch |err| switch (err) {
            error.@"No results" => return null,
            else => return err,
        };
    }
    return try cur.result_set.?.columnNames();
}
