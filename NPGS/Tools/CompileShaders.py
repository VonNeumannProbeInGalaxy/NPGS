import subprocess
import time
from pathlib import Path
from datetime import datetime

# 在文件顶部添加一个新的函数
def get_shader_hash(source_file: Path, macros: list[str] = None) -> str:
    """计算着色器及其配置的哈希值"""
    import hashlib
    
    # 初始化哈希对象
    hasher = hashlib.md5()
    
    # 添加源文件内容到哈希
    with open(source_file, 'rb') as f:
        hasher.update(f.read())
    
    # 添加宏定义到哈希
    if macros:
        hasher.update(''.join(sorted(macros)).encode())
    
    return hasher.hexdigest()

def save_shader_hash(target_file: Path, hash_value: str):
    """保存着色器的哈希值到同目录下的元数据文件"""
    meta_file = target_file.with_suffix(target_file.suffix + '.meta')
    with open(meta_file, 'w') as f:
        f.write(hash_value)

def load_shader_hash(target_file: Path) -> str:
    """加载着色器的哈希值"""
    meta_file = target_file.with_suffix(target_file.suffix + '.meta')
    try:
        with open(meta_file, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""

# 着色器类型及其文件扩展名
SHADER_TYPES = {
    '.comp.glsl': 'compute',
    '.frag.glsl': 'fragment',
    '.geom.glsl': 'geometry',
    '.mesh.glsl': 'mesh',
    '.rahit.glsl': 'ray any hit',
    '.rcall.glsl': 'ray callable',
    '.rchit.glsl': 'ray closest hit',
    '.rgen.glsl': 'ray generation',
    '.rint.glsl': 'ray intersection',
    '.rmiss.glsl': 'ray miss',
    '.task.glsl': 'task',
    '.tesc.glsl': 'tessellation control',
    '.tese.glsl': 'tessellation evaluation',
    '.vert.glsl': 'vertex',
}

# 配置
SOURCE_DIR = Path(__file__).parent.parent / 'Sources' / 'Engine' / 'Shaders'
TARGET_DIR = SOURCE_DIR.parent.parent.parent / 'Assets' / 'Shaders'
GLSLC_PATH = 'glslc.exe'

def parse_includes(shader_file: Path, included_files: set = None) -> set:
    """解析着色器文件中的所有 #include 指令"""
    if included_files is None:
        included_files = set()
    
    shader_dir = shader_file.parent
    try:
        with open(shader_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip().startswith('#include'):
                    # 提取包含文件的路径
                    include_path = line.split('"')[1]
                    full_path = (shader_dir / include_path).resolve()
                    
                    if (full_path not in included_files):
                        included_files.add(full_path)
                        # 递归解析包含的文件
                        parse_includes(full_path, included_files)
    except Exception as e:
        print(f"警告: 解析包含文件时出错 {shader_file.name}: {str(e)}")
    
    return included_files

# 修改 needs_recompile 函数
def needs_recompile(source_file: Path, spv_file: Path, macros: list[str] = None) -> bool:
    """检查源文件及其依赖是否需要重新编译"""
    if not spv_file.exists():
        return True
    
    # 计算当前的哈希值
    current_hash = get_shader_hash(source_file, macros)
    # 获取上次编译时的哈希值
    saved_hash = load_shader_hash(spv_file)
    
    # 如果哈希值不匹配，需要重新编译
    if current_hash != saved_hash:
        return True
    
    # 检查所有包含的文件
    try:
        included_files = parse_includes(source_file)
        target_time = spv_file.stat().st_mtime
        for include_file in included_files:
            if include_file.stat().st_mtime > target_time:
                return True
    except Exception as e:
        print(f"警告: 检查依赖文件时出错 {source_file.name}: {str(e)}")
        return True
    
    return False

class ShaderVariant:
    """着色器变体配置"""
    def __init__(self, input_path: str, output_name: str, macros: list[str]):
        self.input_path = input_path
        self.output_name = output_name
        self.macros = macros

def load_shader_config(config_path: Path) -> list[ShaderVariant]:
    """加载着色器配置文件"""
    variants = []
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('//'):
                    continue
                    
                parts = line.split()
                if len(parts) >= 2:
                    input_path = parts[0]
                    output_name = parts[1]
                    macros = parts[2:] if len(parts) > 2 else []
                    variants.append(ShaderVariant(input_path, output_name, macros))
    except Exception as e:
        print(f"错误: 无法读取配置文件 {config_path}: {str(e)}")
    return variants

# 修改 compile_shader 函数，在编译成功后保存哈希值
def compile_shader(source_file: Path, target_file: Path, macros: list[str] = None) -> bool:
    """编译着色器文件"""
    target_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        cmd = [GLSLC_PATH, '--target-env=vulkan1.4', '-O']
        
        # 添加宏定义
        if macros:
            for macro in macros:
                # 直接添加 -D 前缀到宏定义
                cmd.append(f'-D{macro}')
        
        cmd.extend([str(source_file), '-o', str(target_file)])
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            rel_path = source_file.relative_to(SOURCE_DIR)
            print(f"{result.stderr}")
            return False

        # 保存编译配置的哈希值
        save_shader_hash(target_file, get_shader_hash(source_file, macros))
        print(f"生成 {target_file.name}")
        return True
    except Exception as e:
        rel_path = source_file.relative_to(SOURCE_DIR)
        print(f"{rel_path}: error: {str(e)}")
        return False

# 在 main 函数中修改调用
def main() -> tuple:
    """主函数"""
    current_time = datetime.now().strftime("%H:%M")
    print(f"生成开始于 {current_time}...")
    print("------ 正在编译着色器 ------")
    
    compiled_count = 0
    skipped_count = 0
    failed_count = 0
    
    # 用于跟踪已处理的源文件
    processed_sources = set()
    
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    
    variants = []
    config_file = Path(__file__).parent / 'CompileShaders.cfg'
    if config_file.exists():
        # 处理配置文件中的变体
        variants = load_shader_config(config_file)
        for variant in variants:
            source_file = SOURCE_DIR / variant.input_path
            target_file = TARGET_DIR / variant.output_name
            
            if not source_file.exists():
                print(f"错误: 源文件不存在 {source_file}")
                failed_count += 1
                continue
            
            # 记录已处理的源文件
            processed_sources.add(source_file)
                
            if needs_recompile(source_file, target_file, variant.macros):
                print(f"编译 {source_file.name}")
                if compile_shader(source_file, target_file, variant.macros):
                    compiled_count += 1
                else:
                    failed_count += 1
            else:
                skipped_count += 1
    
    # 处理普通着色器文件
    for shader_ext in SHADER_TYPES.keys():
        for source_file in SOURCE_DIR.rglob(f"*{shader_ext}"):
            # 跳过已经处理过的文件
            if source_file in processed_sources:
                continue
                
            rel_path = source_file.relative_to(SOURCE_DIR)
            base_name = source_file.name.replace('.glsl', '')
            target_file = TARGET_DIR / rel_path.parent / f"{base_name}.spv"
            
            if needs_recompile(source_file, target_file):
                print(f"编译 {source_file.name} -> {target_file.name}")
                if compile_shader(source_file, target_file):
                    compiled_count += 1
                else:
                    failed_count += 1
            else:
                skipped_count += 1

    return compiled_count, failed_count, skipped_count

if __name__ == "__main__":
    start_time = time.time()
    compiled, failed, skipped = main()
    elapsed_time = time.time() - start_time
    
    print(f"========== 生成: {compiled} 成功，{failed} 失败，{skipped} 最新，0 已跳过 ==========")
    print(f"========== 生成 于 {datetime.now().strftime('%H:%M')} 完成，耗时 {elapsed_time:.3f} 秒 ==========")
