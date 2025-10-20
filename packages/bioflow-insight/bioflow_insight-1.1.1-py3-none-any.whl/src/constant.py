#==========================
#    CONSTANT VARIABLES
#==========================

WHILE_UPPER_BOUND = 1000000

ERROR_WORDS = ['null', "params", "log", "workflow", "it", "config"]

ERROR_WORDS_ORIGINS = ['channel', 'Channel', 'null', "params", "logs", "workflow", "log",
                       "false", "true", "False", "True", 
                       "it", "config"]

ILLEGAL_IMPORTS = ["groovy", "java"]

LIST_AS = ["as ", "As ", "AS ", "aS "]

LIST_OPERATORS = ["distinct", "filter", "first", "last", "randomSample", "take", "unique", 
                          "until","buffer","collate","collect","flatten","flatMap","groupBy","groupTuple","map","toList","toSortedList","transpose",
                          "splitCsv","splitFasta","splitFastq","splitText",
                          "cross","collectFile","combine","concat","join","merge","mix","phase","spread","tap",
                          "branch","choice","multiMap","into","separate","tap",
                          "count","countBy","min","max","sum","toInteger",
                          "close","dump","ifEmpty","print","println","set","view", 
                          "map_modified","reduce_modified", "flatMap_modified", "view_modified", "ifEmpty_modified", #The articifiel operations
                          "empty", "of", "fromPath", "fromList", "subscribe", "value", "from"]#This last line is added by me:)

TOOLS = [
    "samtools",
    "bcftools",
    "fastqc",
    "bedtools",
    "multiqc",
    "gatk",
    "bwa",
    "minimap2",
    "tabix",
    "vcf",
    "wget",
    "bgzip",
    "hmmsearch",
    "pigz",
    "picard",
    "star",
    "iqtree",
    "idxstats",
]


#==========================
#         PATTERNS
#==========================

#         CALLS
#--------------------------
BEGINNING_CALL = r"\s(\w+)\s*\("
CALL_ID = r"Call_\d+"
END_CALL = r'\s*\('

#         CHANNEL
#--------------------------
CHANNEL_TAB = r"(\w+) *\[[ \d\'\"]+\]"


#          EMIT
#--------------------------
EMIT_ALONE = r"(\w+)\s*\.\s*(output|out)[^\w]"
EMIT_ALONE_2 = r"(\w+)\s*\.\s*(output|out)[^\w]"
EMIT_EQUALS = r"\w+\s*=\s*((\w+)\s*\.\s*(output|out))[^\w]"
EMIT_NAME = r'(\w+)\s*\.\s*(output|out)\s*\.\s*(\w+)'
EMIT_OPERATION = r"((\w+)\s*\.\s*(output|out))\s*[^\w]"
EMIT_TAB = r'(\w+)\s*\.\s*(output|out)\s*\[\s*(\d+)\s*\]'
TUPLE_EMIT = r'\( *\w+( *\, *\w+)+ *\) *= *'+EMIT_ALONE


#        FUNCTION
#--------------------------
HEADER_FUNCTION = r"(def)\s*(\w+)\s*\([^,)]*(,[^,)]+)*\)\s*{"

#         GENERAL
#--------------------------
DOUBLE_BACKSLAPSH_JUMP = r"\\\\\s*\n\s*"
BACKSLAPSH_JUMP = r"\\\s*\n\s*"
JUMP_DOT = r"\s*\n\s*\."
NUMBER = r"\d+"
TUPLE_EQUALS = r"(\n|;)\s*(\( *\w+( *, *\w+)+ *\) *=)"
WORD = r'\w+'
WORD_EQUALS = r"(\w+)\s*="
WORD_EQUALS_2 = r"(\n|;)\s*(\w+ *=)"
WORD_DOT = r'\w+\s*\.'

LIST_EQUALS = [TUPLE_EQUALS, WORD_EQUALS_2]

#         IMPORTS
#--------------------------
START_IMPORT = r'import\s+'

#         INLUCES
#--------------------------
FULL_INCLUDE = r"include *({([^\}]+)}| +(\w+)) +from +([^\n ]+)"
FULL_INLCUDE_2 = r"include *({([^\}]+)}| +(\w+)| +(\w+ +(as|As|AS|aS) +\w+)) +from +([^\n ]+)"
INCLUDE_AS = r"(\w+) +(as|AS|As|aS) +(\w+)"

#        OPERATION
#--------------------------
CHANNEL_EQUALS = r'\w+\s*=\s*(\w+)'
CHANNEL_EQUALS_LIST = r'\w+\s*=\s*\[(.+)\]'
CHANNEL_EQUALS_OPERATION = r'\w+\s*=\s*(\w+)\s*\.'
CHANNEL_EQUALS_SOMETHING = r"\w+\s*=(.|\s)+"
DOT_OPERATOR = r"\.\s*(\w+)\s*(\(|{)"
DOUBLE_DOT = r"(\w+)\s*=\s*([^\?\n]+)\s*\?([^\n]+)"
DOUBLE_DOT_TUPLE = r"\(\s*\w+\s*(,\s*\w+\s*)+\)\s*=\s*([^\?\n]+)\s*\?([^\n]+)"
END_OPERATOR = r' *(\(|{)'
ILLEGAL_CHARCTER_BEFORE_POTENTIAL_CHANNELS = r"\w|\'|\"|\."
ILLEGAL_CHARCTER_AFTER_POTENTIAL_CHANNELS = r"\w"
MERGE_OPERATIONS = r'\.\s*((merge|mix|concat|spread|join|phase|cross|combine|fromList|collect|fromPath|value|from|fromFilePairs)\s*(\(|\{))'#I've added map to this list cause channels can appear in map can concatenating channels -> it's a strange way of doing it
OPERATOR_IN_PIPE = r"\w+ *{[^}]*}|\w+ *\([^\)]*\)|\w+"
SET_OPERATORS = ["choice", "separate", "tap", "into", "set"]
TUPLE_EQUALS = r'\( *\w+( *, *\w+)+ *\) *=\s*(\w+)\s*\.'
TUPLE_EQUALS_SOMETHING = r"(\( *\w+( *, *\w+)+ *\)) *=(.|\s)+"

#           PIPE
#--------------------------
BEGINNING_PIPE_OPERATOR = r"[\w\.\[\]]+(\s+\|\s+\w+)+"
END_PIPE_OPERATOR = r"\s*(\s*\|\s*\w+)+"


#         PROCESS
#--------------------------
FILE1 = r'file +(\w+) *\n'
FILE2 = r'file *\( *(\w+) *\) *\n'
PATH1 = r'path +(\w+) *\n'
PATH2 = r'path *\( *(\w+) *\) *\n'
FROM = r'[^\w]from ([^\n]+)\n'
INPUT = r"\n\s*input *:"
INTO = r'into +([\w, ]+)'
INTO_2 = r'into +\(?( *\w+ *(, *\w+)*) *\)?'
OUTPUT = r"\n\s*output *:"
PROCESS_HEADER = r'process\s+(\w+|\'[\w ]+\'|\"[\w ]+\")\s*{'
SCRIPT = r"\n\s*script *:|shell *:|exec *:|\"\"\"\s|\'\'\'\s"
WHEN = r"\n\s*when *:"


#       SUBWORKFLOW
#--------------------------
EMIT_SUBWORKFLOW = r"emit *\:"
MAIN = r"\smain *\:\s"
TAKE = r"take *\:"
SUBWORKFLOW_HEADER = r'workflow +(\w+|\'[\w ]+\'|\"[\w ]+\") *{'

#         WORKFLOW
#--------------------------
WORKFLOW_HEADER = r"workflow\s*\{"
WORKFLOW_HEADER_2 = r'[^\w](workflow\s*{)'


#         MONTHS
#--------------------------
month_mapping = {
    'Jan': '01',
    'Feb': '02',
    'Mar': '03',
    'Apr': '04',
    'May': '05',
    'Jun': '06',
    'Jul': '07',
    'Aug': '08',
    'Sep': '09',
    'Oct': '10',
    'Nov': '11',
    'Dec': '12'
}