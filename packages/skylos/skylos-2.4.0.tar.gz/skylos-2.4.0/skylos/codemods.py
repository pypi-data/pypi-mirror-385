from __future__ import annotations
import libcst as cst
from libcst.metadata import PositionProvider
from libcst.helpers import get_full_name_for_node

class _CommentOutBlock(cst.CSTTransformer):

    METADATA_DEPENDENCIES = (PositionProvider,)

    def __init__(self, module_code, marker = "SKYLOS DEADCODE"):
        self.module_code = module_code.splitlines(True)
        self.marker = marker

    def _comment_block(self, start_line, end_line):
        lines = self.module_code[start_line - 1:end_line]
        out = []
        out.append(cst.EmptyLine(comment=cst.Comment(f"# {self.marker} START (lines {start_line}-{end_line})")))
        for raw in lines:
            out.append(cst.EmptyLine(comment=cst.Comment("# " + raw.rstrip("\n"))))
        out.append(cst.EmptyLine(comment=cst.Comment(f"# {self.marker} END")))
        return out

class _CommentOutFunctionAtLine(_CommentOutBlock):
    def __init__(self, func_name, target_line, module_code, marker):
        super().__init__(module_code, marker)
        self.func_name = func_name
        self.target_line = target_line
        self.changed = False

    def _is_target(self, node: cst.CSTNode):
        pos = self.get_metadata(PositionProvider, node, None)
        return pos and pos.start.line == self.target_line

    def leave_FunctionDef(self, orig: cst.FunctionDef, updated: cst.FunctionDef):
        target = self.func_name.split(".")[-1]
        if self._is_target(orig) and (orig.name.value == target):
            self.changed = True
            pos = self.get_metadata(PositionProvider, orig)
            return cst.FlattenSentinel(self._comment_block(pos.start.line, pos.end.line))
        return updated

    def leave_AsyncFunctionDef(self, orig: cst.AsyncFunctionDef, updated: cst.AsyncFunctionDef):
        target = self.func_name.split(".")[-1] 
        if self._is_target(orig) and (orig.name.value == target):
            self.changed = True
            pos = self.get_metadata(PositionProvider, orig)
            return cst.FlattenSentinel(self._comment_block(pos.start.line, pos.end.line))
        return updated

class _CommentOutImportAtLine(_CommentOutBlock):

    def __init__(self, target_name, target_line, module_code, marker):
        super().__init__(module_code, marker)
        self.target_name = target_name
        self.target_line = target_line
        self.changed = False

    def _is_target_line(self, node: cst.CSTNode):
        pos = self.get_metadata(PositionProvider, node, None)
        return bool(pos and (pos.start.line <= self.target_line <= pos.end.line))

    def _render_single_alias_text(self, head, alias: cst.ImportAlias, is_from):
        if is_from:
            alias_txt = alias.name.code
            if alias.asname:
                alias_txt += f" as {alias.asname.name.value}"
            return f"from {head} import {alias_txt}"
        else:
            alias_txt = alias.name.code
            if alias.asname:
                alias_txt += f" as {alias.asname.name.value}"
            return f"import {alias_txt}"

    def _split_aliases(self, aliases, head, is_from):
        kept = []
        removed_for_comment= []
        for alias in list(aliases):
            bound = _bound_name_for_import_alias(alias)
            name_code = get_full_name_for_node(alias.name)
            tail = name_code.split(".")[-1]
            if self.target_name in (bound, tail):
                self.changed = True
                removed_for_comment.append(self._render_single_alias_text(head, alias, is_from))
            else:
                kept.append(alias)
        return kept, removed_for_comment

    def leave_Import(self, orig: cst.Import, updated: cst.Import):
        if not self._is_target_line(orig):
            return updated
        
        head = "" 
        kept, removed = self._split_aliases(updated.names, head, is_from=False)
        
        if not removed:
            return updated
        
        pos = self.get_metadata(PositionProvider, orig)
        if not kept:
            return cst.FlattenSentinel(self._comment_block(pos.start.line, pos.end.line))
        
        commented = []
        for txt in removed:
            comment = cst.Comment(f"# {self.marker}: {txt}")
            commented.append(cst.EmptyLine(comment=comment))

        kept_import = updated.with_changes(names=tuple(kept))
        all_nodes = [kept_import] + commented
        return cst.FlattenSentinel(all_nodes)

    def leave_ImportFrom(self, orig: cst.ImportFrom, updated: cst.ImportFrom):
        if not self._is_target_line(orig) or isinstance(updated.names, cst.ImportStar):
            return updated
        
        if updated.relative:
            dots = "." * len(updated.relative)
        else:
            dots = ""

        if updated.module is not None:
            modname = updated.module.code
        else:
            modname = ""

        mod = f"{dots}{modname}"

        kept, removed = self._split_aliases(list(updated.names), mod, is_from=True)
        
        if not removed:
            return updated
        pos = self.get_metadata(PositionProvider, orig)
        
        if not kept:
            comment_block = self._comment_block(pos.start.line, pos.end.line)
            return cst.FlattenSentinel(comment_block)

        commented = []
        for txt in removed:
            comment = cst.Comment(f"# {self.marker}: {txt}")
            commented.append(cst.EmptyLine(comment=comment))

        updated_import = updated.with_changes(names=tuple(kept))
        all_nodes = [updated_import] + commented

        return cst.FlattenSentinel(all_nodes)

def comment_out_unused_function_cst(code, func_name, line_number, marker = "SKYLOS DEADCODE"):
    wrapper = cst.MetadataWrapper(cst.parse_module(code))
    tx = _CommentOutFunctionAtLine(func_name, line_number, code, marker)
    new_mod = wrapper.visit(tx)
    return new_mod.code, tx.changed

def comment_out_unused_import_cst(code, import_name, line_number, marker = "SKYLOS DEADCODE"):
    wrapper = cst.MetadataWrapper(cst.parse_module(code))
    tx = _CommentOutImportAtLine(import_name, line_number, code, marker)
    new_mod = wrapper.visit(tx)
    return new_mod.code, tx.changed

def _bound_name_for_import_alias(alias: cst.ImportAlias):
    if alias.asname:
        return alias.asname.name.value
    node = alias.name
    while isinstance(node, cst.Attribute):
        node = node.value
    return node.value 

class _RemoveImportAtLine(cst.CSTTransformer):
    METADATA_DEPENDENCIES = (PositionProvider,)

    def __init__(self, target_name, target_line):
        self.target_name = target_name
        self.target_line = target_line
        self.changed = False

    def _is_target_line(self, node: cst.CSTNode):
        pos = self.get_metadata(PositionProvider, node, None)
        return bool(pos and (pos.start.line <= self.target_line <= pos.end.line))
    
    def _filter_aliases(self, aliases):
        kept = []
        for alias in aliases:
            bound = _bound_name_for_import_alias(alias)
            name_code = get_full_name_for_node(alias.name) or ""
            tail = name_code.split(".")[-1]
            if self.target_name in (bound, tail):
                self.changed = True
                continue
            kept.append(alias)
        return kept

    def leave_Import(self, orig: cst.Import, updated: cst.Import):
        if not self._is_target_line(orig):
            return updated
        kept = self._filter_aliases(updated.names)
        if not kept:
            return cst.RemoveFromParent()
        return updated.with_changes(names=tuple(kept))

    def leave_ImportFrom(self, orig: cst.ImportFrom, updated: cst.ImportFrom):
        if not self._is_target_line(orig):
            return updated
        if isinstance(updated.names, cst.ImportStar):
            return updated 
        kept = self._filter_aliases(list(updated.names))
        if not kept:
            return cst.RemoveFromParent()

        return updated.with_changes(names=tuple(kept))

class _RemoveFunctionAtLine(cst.CSTTransformer):
    METADATA_DEPENDENCIES = (PositionProvider,)

    def __init__(self, func_name, target_line):
        self.func_name = func_name
        self.target_line = target_line
        self.changed = False

    def _is_target(self, node: cst.CSTNode):
        pos = self.get_metadata(PositionProvider, node, None)
        return pos and pos.start.line == self.target_line

    def leave_FunctionDef(self, orig: cst.FunctionDef, updated: cst.FunctionDef):
        target = self.func_name.split(".")[-1]
        if self._is_target(orig) and (orig.name.value == target):
            self.changed = True
            return cst.RemoveFromParent()
        return updated

    def leave_AsyncFunctionDef(self, orig: cst.AsyncFunctionDef, updated: cst.AsyncFunctionDef):
        target = self.func_name.split(".")[-1]
        if self._is_target(orig) and (orig.name.value == target):
            self.changed = True
            return cst.RemoveFromParent()

        return updated

def remove_unused_import_cst(code, import_name, line_number):
    wrapper = cst.MetadataWrapper(cst.parse_module(code))
    tx = _RemoveImportAtLine(import_name, line_number)
    new_mod = wrapper.visit(tx)
    return new_mod.code, tx.changed

def remove_unused_function_cst(code, func_name, line_number):
    wrapper = cst.MetadataWrapper(cst.parse_module(code))
    tx = _RemoveFunctionAtLine(func_name, line_number)
    new_mod = wrapper.visit(tx)
    return new_mod.code, tx.changed
