import logging
import os
import langchain

# 是否显示详细日志
import nltk

log_verbose = False
langchain.verbose = False

# 通常情况下不需要更改以下内容

# 日志格式
LOG_FORMAT = "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s"
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(format=LOG_FORMAT)

# nltk 添加路径
nltk.data.path.append("nltk_data/")

# 日志存储路径
LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
if not os.path.exists(LOG_PATH):
    os.mkdir(LOG_PATH)

# infobase 不加载的目录下的文件夹，文件类型
# 支持文件夹名称或者文件名称正则表达
IGNORE_PATH = ["*.class", "*.ear", "*.jar", "*.jws", "*.ser", "*.war", ".classpath", ".cosine", ".eclipse", ".git",
               ".gradle", ".idea", ".mvn", ".project", ".settings", ".vscode", "bin", "doc", "build", "logs", "out",
               "target", ".*", "LICENSE", "test", "*.json", "*.xlsx", "*.xls", "resource"]

# 不用语言，通过tree-sitter解析出来的语法树之后，哪些是需要保留的类型：
SUPPORT_LANGUAGE_DEFINITION_TYPE = {
    "java": {
        "definition_list": ["module", "program", "class_declaration", "class_body", "method_declaration"],
        "mini_analysis_type": "method_declaration",
        "ignore_save_type": ["class_body", "program"]
    },
    "python": {
        "definition_list": ["module", "class_definition", "function_definition", "block", "def"],
        "mini_analysis_type": "function_definition",
        "ignore_save_type": ["block", "def"]
    }
}

CODE_TYPE_FILE_SUFFIX_MAPPING = {
    "java": ".java",
    "python": ".py"
}

# 向量数据库配置：
# 向量数据库存储路径
PERSIST_DIRECTORY = "data/chroma_db"
# 倒排索引存入的文件路径
INVERTED_INDEX_FILE_PATH = "data/lexical_inverted_index.pickle"
# top-k
SIMILARITY_SEARCH_TOP_K = 8

# 项目路径，如果可以应该存入数据库中
# PROJECT_PATH = "/Users/zhanbei/IdeaProjects/doop-server"
# PROJECT_PATH = "/Users/zhanbei/IdeaProjects/EvalEx/"
PROJECT_PATH = "/Users/zhanbei/IdeaProjects/doop-server"

FILE_THRESHOLD = 100
