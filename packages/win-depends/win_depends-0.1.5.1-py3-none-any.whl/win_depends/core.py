import os
import pefile
from tqdm import tqdm
from .graph import DependencyGraph
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import lru_cache


@lru_cache(maxsize=1)
def get_system_search_paths():
    return [p for p in os.environ.get("PATH", "").split(os.pathsep) if os.path.isdir(p)]


class DependencyParseItem:
    def __init__(self, path, missing, invalid, delay_loaded, is_system):
        self.path = path
        self.missing = missing
        self.invalid = invalid
        self.delay_loaded = delay_loaded
        self.is_system = is_system


class DependencyParseResult:
    def __init__(self):
        self.items = []

    def add(self, *args, **kwargs):
        self.items.append(DependencyParseItem(*args, **kwargs))

    def __iter__(self):
        return iter(self.items)


@lru_cache(maxsize=1024)
def find_local_dll(base_dir, dll):
    temp_path = os.path.abspath(os.path.join(base_dir, dll))
    if os.path.isfile(temp_path):
        return temp_path
    return None


@lru_cache(maxsize=1024)
def find_system_dll(dll):
    for sys_path in get_system_search_paths():
        temp_path = os.path.abspath(os.path.join(sys_path, dll))
        if os.path.isfile(temp_path):
            return temp_path
    return None


def parse_file_for_dependencies(base_dir, base_file):
    result = DependencyParseResult()

    pe_base = pefile.PE(base_file, fast_load=True)
    pe_base.parse_data_directories(1)
    pe_base_imports = getattr(pe_base, "DIRECTORY_ENTRY_IMPORT", [])
    pe_base_delay_imports = getattr(pe_base, "DIRECTORY_ENTRY_DELAY_IMPORT", [])
    pe_base_bound_imports = getattr(pe_base, "DIRECTORY_ENTRY_BOUND_IMPORT", [])

    for entries in pe_base_imports, pe_base_delay_imports, pe_base_bound_imports:
        for entry in entries:
            entry_name = entry.dll.decode(errors="ignore")
            entry_imports_set = set([i.ordinal for i in entry.imports])
            entry_imports_set.remove(None) if None in entry_imports_set else None
            # 重试本地查找文件
            dll_local = find_local_dll(base_dir, entry_name)
            # 尝试系统路径查找文件
            dll_system = find_system_dll(entry_name)

            dll_is_missing = not dll_local and not dll_system
            dll_is_delay = entry in pe_base_delay_imports
            dll_is_system = dll_system is not None and dll_local is None

            if not dll_is_missing:
                dll_path = dll_local if dll_local else dll_system
                pe_dep = pefile.PE(dll_path, fast_load=True)
                pe_dep.parse_data_directories(0)
                pe_dep_exports = getattr(pe_dep, "DIRECTORY_ENTRY_EXPORT", [])
                dep_export_set = set([i.ordinal for i in pe_dep_exports.symbols])
                dep_export_set.remove(None) if None in dep_export_set else None

                dll_is_valid = entry_imports_set.issubset(dep_export_set)

                result.add(
                    dll_path,
                    dll_is_missing,
                    not dll_is_valid,
                    dll_is_delay,
                    dll_is_system,
                )
            else:
                result.add(entry_name, True, False, False, False)

    pe_base.close()
    return result


def _build_dependency_graph(root_files, detect_system=False, verbose=False, threads=16):
    pbar = tqdm(total=0, desc="Resolving dependencies", unit="file", dynamic_ncols=True)
    abs_files = [os.path.abspath(path) for path in root_files]
    base_dir = os.path.dirname(abs_files[0])
    graph = DependencyGraph()
    submitted = set()

    with ProcessPoolExecutor(max_workers=threads) as executor:
        futures = {}

        def submit(path):
            future = executor.submit(parse_file_for_dependencies, base_dir, path)
            futures[future] = path
            pbar.total += 1
            pbar.refresh()
            if verbose:
                print(f"[DEBUG] Submitting: {path}")

        for abs_file in abs_files:
            submitted.add(abs_file)
            submit(abs_file)

        while futures:
            # 使用as_completed保证并发性能
            for future in as_completed(list(futures.keys())):
                parent_path = futures.pop(future)

                try:
                    results = future.result()
                except Exception as e:
                    if verbose:
                        print(f"[ERROR] Failed to parse {parent_path}: {e}")
                    results = DependencyParseResult()

                for child_item in results:
                    # 如果是系统文件, 并且存在, 并且设置为不检测, 那么跳过
                    # 对于不存在的系统文件, 仍然要显示
                    if (
                        child_item.is_system
                        and not detect_system
                        and not child_item.missing
                    ):
                        # if verbose:
                        # print(f"[DEBUG] Because of no detect system, Skip {child_item.path} for {parent_path}")
                        continue
                    graph.add_edge(
                        parent_path,
                        child_item.path,
                        delay_loaded=child_item.delay_loaded,
                        missing=child_item.missing,
                        invalid=child_item.invalid,
                    )
                    child_node = graph.get_node(child_item.path)
                    child_node.is_system = child_item.is_system
                    # 如果这个对象丢失, 那么不要继续展开, 没有意义
                    if child_item.missing:
                        if verbose:
                            print(
                                f"[DEBUG] Missing dependency {child_item.path} for {parent_path}"
                            )
                        continue
                    if child_node.path not in submitted:
                        submitted.add(child_node.path)
                        submit(child_node.path)
                pbar.update(1)
                break

    for node in graph.nodes.values():
        if node.path.lower().endswith(".dll") and not graph.parents.get(node):
            node.orphan = True

    pbar.close()
    return graph


def build_dependency_graph(path, detect_system=False, verbose=False, threads=16):
    abs_path = os.path.abspath(path)
    if os.path.isdir(abs_path):
        files = [
            os.path.abspath(os.path.join(abs_path, e.name))
            for e in os.scandir(abs_path)
            if e.is_file() and e.name.lower().endswith((".dll", ".exe"))
        ]
    else:
        files = [abs_path]
    return _build_dependency_graph(files, detect_system, verbose, threads)


def print_orphan(graph):
    orphans = sorted(
        [
            node
            for node in getattr(graph, "nodes", {}).values()
            if getattr(node, "orphan", False)
        ],
        key=lambda n: n.path.lower(),
    )
    if orphans:
        print("🧩 Orphan DLLs:")
        for node in orphans:
            print(f"  🧩 {os.path.basename(node.path)}")
    else:
        print("🧩 No orphan DLLs.")


def print_missing(graph):
    missing = {
        edge.child for edge in getattr(graph, "edges", {}).values() if edge.missing
    }
    missing = sorted(missing, key=lambda x: x.path.lower())
    if not missing:
        print("✅ No missing dependencies.")
        return
    print("❌ Missing dependencies:")
    for node in missing:
        print(f"  ❌ {os.path.basename(node.path)}")
        for p in getattr(graph, "parents", {}).get(node, []):
            print(f"    ↳ Required by: {os.path.basename(p.path)}")


def print_invalid(graph):
    invalid = {
        edge.child for edge in getattr(graph, "edges", {}).values() if edge.invalid
    }
    invalid = sorted(invalid, key=lambda x: x.path.lower())
    if not invalid:
        print("✅ No invalid files.")
        return
    print("❗ Invalid files (failed to parse):")
    for node in invalid:
        print(f"  ❗ {os.path.basename(node.path)}")
        children = getattr(graph, "children", {}).get(node, [])
        if children:
            for c in children:
                print(f"    ↳ Tried to load: {os.path.basename(c.path)}")
        else:
            print("    ↳ No dependencies parsed.")
