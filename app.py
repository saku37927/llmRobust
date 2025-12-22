# prompt特征向量维度
# 0 文体
# 1 句型
# 2 语义模糊度
# 3 语言文化风格
# 4 语法复杂度
# 5 词汇复杂度
# 6 长度
# 7 歧义性
# 8 冗余度
# 9 语法流畅性
# 10 反向输出
# 11 情绪刺激性
# 12 语态
# 13 时态
# 14 情态
# 15 无关信息量
# 16 否定词含量
# 17 思维链格式
# 18 是否有例子

# corpus特征向量维度
# 0 语法复杂度
# 1 词汇复杂度
# 2 长度
# 3 冗余度
# 4 极性词数量
# 5 词汇多样性
# 6 句型
# 7 时态
# 8 语态
# 9 标点
# 10 特殊字符
# 11 语义模糊度
# 12 文体
# 13 语言文化风格
# 14 领域


112

# 特征名称映射
PROMPT_FEATURE_NAMES = {
    0: '文体',
    1: '句型', 
    2: '语义模糊度',
    3: '语言文化风格',
    4: '语法复杂度',
    5: '词汇复杂度',
    6: '长度',
    7: '歧义性',
    8: '冗余度',
    9: '语法流畅性',
    10: '反向输出',
    11: '情绪刺激性',
    12: '语态',
    13: '时态',
    14: '情态',
    15: '无关信息量',
    16: '否定词含量',
    17: '思维链格式',
    18: '是否有例子'
}

CORPUS_FEATURE_NAMES = {
    0: '语法复杂度',
    1: '词汇复杂度',
    2: '长度',
    3: '冗余度',
    4: '极性词数量',
    5: '词汇多样性',
    6: '句型',
    7: '时态',
    8: '语态',
    9: '标点',
    10: '特殊字符',
    11: '语义模糊度',
    12: '文体',
    13: '语言文化风格',
    14: '领域'
}

from flask import Flask, jsonify, request
from flask_cors import CORS
import random
import json
import os
from collections import defaultdict
import numpy as np
from scipy import stats  # 添加这行导入
from sklearn.manifold import TSNE

app = Flask(__name__)
CORS(app)

# 配置文件路径
PROMPT_FILE_PATH = r"D:\Desktop\LLM_Robust_Front\data\prompt\prompt_sorted.json"
CORPUS_FILE_PATH = r"D:\Desktop\LLM_Robust_Front\data\corpus\corpus_sorted.json"

# 加载数据文件
with open(r'D:\Desktop\LLM_Robust_Front\data\feature\prompt_feature_updated_final.json', 'r') as f:
    prompt_features = json.load(f)

with open('D:/Desktop/LLM_Robust_Front/data/feature/corpus_feature_updated.json', 'r') as f:
    corpus_features = json.load(f)

# with open('D:/Desktop/LLM_Robust_Front/data/final_result.json', 'r') as f:

with open(r'D:\Desktop\LLM_Robust_Front\data\flan_output\original\attack_contrast_result.json', 'r') as f:
    final_results = json.load(f)

# 加载各种攻击方式的数据
attack_data = {}
attack_methods = ['charswap', 'deletion', 'easydata', 'embedding', 'swap', 'synonym', 'wordnet']
for method in attack_methods:
    try:
        attack_file_path = os.path.join('data', 'flan_output', 'attack', f'prompt_{method}.json')
        if os.path.exists(attack_file_path):
            with open(attack_file_path, 'r', encoding='utf-8') as f:
                attack_data[method] = json.load(f)
            print(f"成功加载攻击方式 {method} 的数据，包含 {len(attack_data[method])} 条记录")
        else:
            print(f"攻击方式 {method} 的数据文件不存在: {attack_file_path}")
    except Exception as e:
        print(f"加载攻击方式 {method} 的数据失败: {e}")

# 加载嵌入向量（全局只加载一次）
with open(r'D:\Desktop\LLM_Robust_Front\data\embedding\prompt_embeddings.json', 'r') as f:
    prompt_embeddings_data = json.load(f)
prompt_embedding_map = {item['prompt_id']: item['embedding'] for item in prompt_embeddings_data}

with open(r'D:\Desktop\LLM_Robust_Front\data\embedding\corpus_embeddings.json', 'r') as f:
    corpus_embeddings_data = json.load(f)
corpus_embedding_map = {item['corpus_id']: item['embedding'] for item in corpus_embeddings_data}

# 定义离散特征及其可能的值
DISCRETE_FEATURES = {
    '文体': {
        0: '无明显文体特征',
        1: '书面用语',
        2: '口头用语',
        3: '礼貌用语',
        4: '动词短语',
        5: '恶劣用语'
    },
    '句型': {
        0: '无明显特征',
        1: '疑问句',
        2: '祈使句',
        3: '陈述句'
    },
    '语言文化风格': {
        0: '无明显特征',
        1: '美国文化',
        2: '东方文化',
        3: '拉丁文化',
        4: '欧洲文化'
    },
    '反向输出': {
        0: '无',
        1: '有'
    },
    '语态': {
        0: '无',
        1: '第一人称',
        2: '第二人称',
        3: '第三人称'
    },
    '时态': {
        0: '无',
        1: '现在时',
        2: '过去时',
        3: '未来时'
    },
    '情态': {
        0: '无',
        1: 'must',
        2: 'should',
        3: 'may',
        4: 'could',
        5: 'might',
        6: 'can',
        7: 'will',
        8: 'would',
        9: 'shall'
    },
    '思维链格式': {
        0: '无',
        1: '存在思维链格式'
    },
    '是否有例子': {
        0: '无例子',
        1: '有例子',
        2: '多例子'
    }
    
}

# 定义离散特征及其可能的值
CORPUS_DISCRETE_FEATURES = {
    '文体': {
        0: '无明显文体特征',
        1: '书面用语',
        2: '口头用语',
        3: '礼貌用语',
        4: '动词短语',
        5: '恶劣用语'
    },
    '句型': {
        0: '无明显特征',
        1: '疑问句',
        2: '祈使句',
        3: '陈述句'
    },
    '语言文化风格': {
        0: '无明显特征',
        1: '美国文化',
        2: '东方文化',
        3: '拉丁文化',
        4: '欧洲文化'
    },
    '语态': {
        0: '无',
        1: '第一人称',
        2: '第二人称',
        3: '第三人称'
    },
    '时态': {
        0: '无',
        1: '现在时',
        2: '过去时',
        3: '未来时'
    },
    '领域': {
        0: '无明显特征',
        1: '教育',
        2: '科学',
        3: '文化',
        4: '体育'
        }
}

# 定义特征向量中各个维度对应的特征
PROMPT_FEATURE_DIMENSIONS = {
    '文体': 0,
    '句型': 1,
    '语言文化风格': 3,  # 注意: 第4个维度索引是3
    '反向输出': 10,     # 第11个维度索引是10
    '语态': 12,        # 第13个维度索引是12
    '时态': 13,        # 第14个维度索引是13
    '情态': 14,        # 第15个维度索引是14
    '是否有例子': 18,   # 第18个维度索引是17
    '思维链格式': 17    # 第19个维度索引是18
}

CONTINUOUS_FEATURES = {
    '语义模糊度': {'index': 2 },  # 第5个特征(索引4)，分10个区间
    '语法复杂度': {'index': 4},  # 第6个特征(索引5)，分5个区间
    '词汇复杂度': {'index': 5}, 
    '长度': {'index': 6}, 
    '歧义性': {'index': 7}, 
    '冗余度': {'index': 8}, 
    '语法流畅性':{'index': 9},
    '情绪刺激性': {'index': 11}, 
    '无关信息量': {'index': 15}, 
    '否定词含量': {'index': 16}, 
}

CORPUS_FEATURE_DIMENSIONS = {
    '句型': 6,
    '语态': 8,        # 第13个维度索引是12
    '时态': 7,        # 第14个维度索引是13
    '文体': 12,
    '语言文化风格': 13,  # 注意: 第4个维度索引是3
    '领域': 14,        # 第15个维度索引是14
}
CORPUS_CONTINUOUS_FEATURES = {
    '词汇多样性': {'index': 5 },  # 第5个特征(索引4)，分10个区间
    '语法复杂度': {'index': 0},  # 第6个特征(索引5)，分5个区间
    '词汇复杂度': {'index': 1}, 
    '长度': {'index': 2}, 
    '极性词数量': {'index': 4}, 
    '冗余度': {'index': 3}, 
    '标点':{'index': 9},
    '特殊字符': {'index': 10}, 
    '语义模糊度': {'index': 11}, 
}



@app.route('/api/prompt_feature_distribution', methods=['POST'])
def get_prompt_feature_distribution():
    data = request.get_json()
    prompt_ids = data.get('prompt_ids', [])
    corpus_ids = data.get('corpus_ids', [])
    selected_attack_methods = data.get('selected_attack_methods', [])
    
    # 预处理：构建快速查询结构
    prompt_id_set = set(prompt_ids)
    corpus_id_set = set(corpus_ids)
    
    # 构建(prompt_id, corpus_id) -> accuracy的映射
    # 根据前端选择的攻击方式 检索特定攻击下的鲁棒性值
    result_map = {}
    
    if selected_attack_methods and len(selected_attack_methods) > 0:
        # 使用选择的攻击方式数据，从 final_results 中提取对应字段
        for res in final_results:
            if res['prompt_id'] in prompt_id_set and res['corpus_id'] in corpus_id_set:
                key = (res['prompt_id'], res['corpus_id'])
                attack_results = []
                
                # 提取选择的攻击方法的结果
                for method in selected_attack_methods:
                    field_name = f'prompt_{method}_result'
                    if field_name in res:
                        attack_results.append(res[field_name])
                
                # 如果有有效的攻击结果，计算平均值
                if attack_results:
                    avg_accuracy = sum(attack_results) / len(attack_results)
                    result_map[key] = avg_accuracy
    else:
        # 使用原始数据（所有攻击方式的平均）
        result_map = {
            (r['prompt_id'], r['corpus_id']): r['accuracy']
            for r in final_results
            if r['prompt_id'] in prompt_id_set and r['corpus_id'] in corpus_id_set
        }
    
    # 构建prompt_id -> feature_vector的映射
    feature_map = {
        pf['id']: pf['vector']
        for pf in prompt_features
        if pf['id'] in prompt_id_set
    }
    
    # 结果数据结构
    distribution = {
        'discrete': {},
        'continuous': {}
    }
    
    # 1. 处理离散特征
    for feature_name, value_map in DISCRETE_FEATURES.items():
        feature_index = PROMPT_FEATURE_DIMENSIONS[feature_name]  # 假设有预定义的维度映射
        feature_stats = defaultdict(lambda: {
            'count': 0,
            'total_robustness': 0,
            'prompt_ids': []  # 新增：记录属于该特征值的prompt_id
        })
        
        # 统计每个特征值
        for prompt_id, vector in feature_map.items():
            value = vector[feature_index]
            if value in value_map:  # 只统计预定义的特征值
                # 计算该prompt_id在所有corpus_ids下的平均鲁棒性
                accuracies = [
                    result_map[(prompt_id, cid)]
                    for cid in corpus_ids
                    if (prompt_id, cid) in result_map
                ]
                
                if accuracies:
                    avg_robustness = sum(accuracies) / len(accuracies)
                    feature_stats[value]['count'] += 1
                    feature_stats[value]['total_robustness'] += avg_robustness
                    feature_stats[value]['prompt_ids'].append(prompt_id)  # 记录prompt_id
        
        # 整理结果
        discrete_result = []
        for value, value_name in value_map.items():
            stats = feature_stats.get(value, {
                'count': 0,
                'total_robustness': 0,
                'prompt_ids': []
            })
            discrete_result.append({
                'value': value,
                'value_name': value_name,
                'count': stats['count'],
                'avg_robustness': round(stats['total_robustness'] / stats['count'], 4) if stats['count'] > 0 else None,
                'prompt_ids': stats['prompt_ids']  # 新增：返回prompt_id列表
            })
        
        distribution['discrete'][feature_name] = discrete_result
    
    # 2. 处理连续特征（改为返回所有值）
    for feature_name, config in CONTINUOUS_FEATURES.items():
        feature_index = config['index']
        feature_values = []
        
        # 收集所有prompt的该特征值及其鲁棒性
        for prompt_id, vector in feature_map.items():
            value = vector[feature_index]
            
            # 计算该prompt在所有corpus下的平均鲁棒性
            accuracies = [
                result_map[(prompt_id, cid)]
                for cid in corpus_ids
                if (prompt_id, cid) in result_map
            ]
            
            if accuracies:
                avg_robustness = sum(accuracies) / len(accuracies)
                feature_values.append({
                    'value': value,
                    'robustness': avg_robustness,
                    'prompt_id': prompt_id  # 可选，便于追踪数据来源
                })
        
        # 按特征值排序（可选）
        feature_values.sort(key=lambda x: x['value'])
        
        # 计算全局统计量
        values = [x['value'] for x in feature_values]
        robustnesses = [x['robustness'] for x in feature_values]
        
        distribution['continuous'][feature_name] = {
            'values': feature_values,  # 所有原始数据点
            'statistics': {
                'value_mean': np.mean(values) if values else None,
                'value_std': np.std(values) if values else None,
                'robustness_mean': np.mean(robustnesses) if robustnesses else None,
                'robustness_std': np.std(robustnesses) if robustnesses else None,
                'count': len(feature_values)
            }
        }
    
    return jsonify({
        'success': True,
        'distribution': distribution
    })


@app.route('/api/corpus_feature_distribution', methods=['POST'])
def get_corpus_feature_distribution():
    data = request.get_json()
    prompt_ids = data.get('prompt_ids', [])
    corpus_ids = data.get('corpus_ids', [])
    selected_attack_methods = data.get('selected_attack_methods', [])
    
    # 预处理：构建快速查询结构
    prompt_id_set = set(prompt_ids)
    corpus_id_set = set(corpus_ids)
    
    # 构建(prompt_id, corpus_id) -> accuracy的映射
    # 根据前端选择的攻击方式 检索特定攻击下的鲁棒性值
    result_map = {}
    
    if selected_attack_methods and len(selected_attack_methods) > 0:
        # 使用选择的攻击方式数据，从 final_results 中提取对应字段
        for res in final_results:
            if res['prompt_id'] in prompt_id_set and res['corpus_id'] in corpus_id_set:
                key = (res['prompt_id'], res['corpus_id'])
                attack_results = []
                
                # 提取选择的攻击方法的结果
                for method in selected_attack_methods:
                    field_name = f'prompt_{method}_result'
                    if field_name in res:
                        attack_results.append(res[field_name])
                
                # 如果有有效的攻击结果，计算平均值
                if attack_results:
                    avg_accuracy = sum(attack_results) / len(attack_results)
                    result_map[key] = avg_accuracy
    else:
        # 使用原始数据（所有攻击方式的平均）
        result_map = {
            (r['prompt_id'], r['corpus_id']): r['accuracy']
            for r in final_results
            if r['prompt_id'] in prompt_id_set and r['corpus_id'] in corpus_id_set
        }
    
    # 构建corpus_id -> feature_vector的映射
    feature_map = {
        pf['id']: pf['vector']
        for pf in corpus_features
        if pf['id'] in corpus_id_set
    }
    
    # 结果数据结构
    distribution = {
        'discrete': {},
        'continuous': {}
    }
    
    # 1. 处理离散特征
    for feature_name, value_map in CORPUS_DISCRETE_FEATURES.items():
        feature_index = CORPUS_FEATURE_DIMENSIONS[feature_name]
        feature_stats = defaultdict(lambda: {
            'count': 0,
            'total_robustness': 0,
            'corpus_ids': []  # 新增：记录属于该特征值的corpus_id
        })
        
        # 统计每个特征值
        for corpus_id, vector in feature_map.items():
            value = vector[feature_index]
            if value in value_map:
                # 计算该corpus_id在所有prompt_ids下的平均鲁棒性
                accuracies = [
                    result_map[(pid, corpus_id)]
                    for pid in prompt_ids
                    if (pid, corpus_id) in result_map
                ]
                
                if accuracies:
                    avg_robustness = sum(accuracies) / len(accuracies)
                    feature_stats[value]['count'] += 1
                    feature_stats[value]['total_robustness'] += avg_robustness
                    feature_stats[value]['corpus_ids'].append(corpus_id)  # 记录corpus_id
        
        # 整理结果
        discrete_result = []
        for value, value_name in value_map.items():
            stats = feature_stats.get(value, {
                'count': 0,
                'total_robustness': 0,
                'corpus_ids': []
            })
            discrete_result.append({
                'value': value,
                'value_name': value_name,
                'count': stats['count'],
                'avg_robustness': round(stats['total_robustness'] / stats['count'], 4) if stats['count'] > 0 else None,
                'corpus_ids': stats['corpus_ids']  # 新增：返回corpus_id列表
            })
        
        distribution['discrete'][feature_name] = discrete_result
    
    # 2. 处理连续特征（保持不变）
    for feature_name, config in CORPUS_CONTINUOUS_FEATURES.items():
        feature_index = config['index']
        feature_values = []
        
        for corpus_id, vector in feature_map.items():
            value = vector[feature_index]
            
            accuracies = [
                result_map[(pid, corpus_id)]
                for pid in prompt_ids
                if (pid, corpus_id) in result_map
            ]
            
            if accuracies:
                avg_robustness = sum(accuracies) / len(accuracies)
                feature_values.append({
                    'value': value,
                    'robustness': avg_robustness,
                    'corpus_id': corpus_id
                })
        
        feature_values.sort(key=lambda x: x['value'])
        
        values = [x['value'] for x in feature_values]
        robustnesses = [x['robustness'] for x in feature_values]
        
        distribution['continuous'][feature_name] = {
            'values': feature_values,
            'statistics': {
                'value_mean': np.mean(values) if values else None,
                'value_std': np.std(values) if values else None,
                'robustness_mean': np.mean(robustnesses) if robustnesses else None,
                'robustness_std': np.std(robustnesses) if robustnesses else None,
                'count': len(feature_values)
            }
        }
    
    return jsonify({
        'success': True,
        'distribution': distribution
    })



def calculate_prompt_robustness(prompt_ids, corpus_ids, selected_attack_methods=None):
    # 预处理：将列表转换为集合提高查找效率
    prompt_ids_set = set(prompt_ids)
    corpus_ids_set = set(corpus_ids)
    
    # 预处理：构建prompt_id到特征向量的映射
    prompt_feature_map = {
        pf['id']: pf['vector'] 
        for pf in prompt_features 
        if pf['id'] in prompt_ids_set
    }
    
    # 预处理：构建(prompt_id, corpus_id)到accuracy的映射
    # 根据前端选择的攻击方式 检索特定攻击下的鲁棒性值
    result_map = {}
    
    if selected_attack_methods and len(selected_attack_methods) > 0:
        # 使用选择的攻击方式数据，从 final_results 中提取对应字段
        for res in final_results:
            if res['prompt_id'] in prompt_ids_set and res['corpus_id'] in corpus_ids_set:
                key = (res['prompt_id'], res['corpus_id'])
                attack_results = []
                
                # 提取选择的攻击方法的结果
                for method in selected_attack_methods:
                    field_name = f'prompt_{method}_result'
                    if field_name in res:
                        attack_results.append(res[field_name])
                
                # 如果有有效的攻击结果，计算平均值
                if attack_results:
                    avg_accuracy = sum(attack_results) / len(attack_results)
                    result_map[key] = avg_accuracy
        
        # 计算每个组合的平均accuracy
        result_map = {
            key: sum(accuracies) / len(accuracies)
            for key, accuracies in result_map.items()
        }
    else:
        # 使用原始数据（所有攻击方式的平均）
        result_map = {
            (res['prompt_id'], res['corpus_id']): res['accuracy']
            for res in final_results 
            if res['prompt_id'] in prompt_ids_set and res['corpus_id'] in corpus_ids_set
        }
    
    # 结果字典，存储所有离散特征的鲁棒性值
    all_robustness = {}
    
    # 对每个离散特征计算鲁棒性
    for feature_name, feature_values in DISCRETE_FEATURES.items():
        dimension_index = PROMPT_FEATURE_DIMENSIONS[feature_name]
        feature_robustness = {}
        
        # 按特征值分组计算
        value_groups = defaultdict(list)
        for prompt_id, vector in prompt_feature_map.items():
            value = vector[dimension_index]
            if value in feature_values:  # 只处理预定义的特征值
                value_groups[value].append(prompt_id)
        
        # 对每个特征值计算鲁棒性
        for value, value_name in feature_values.items():
            matching_prompt_ids = value_groups.get(value, [])
            
            # 计算所有相关组合的accuracy
            accuracies = [
                result_map[(pid, cid)]
                for pid in matching_prompt_ids
                for cid in corpus_ids
                if (pid, cid) in result_map
            ]
            
            # 计算均值
            if accuracies:
                avg_accuracy = sum(accuracies) / len(accuracies)
                feature_robustness[value_name] = round(avg_accuracy, 2)
            else:
                feature_robustness[value_name] = None
        
        all_robustness[feature_name] = feature_robustness
    
    return all_robustness

def calculate_corpus_robustness(prompt_ids, corpus_ids, selected_attack_methods=None):
    # 预处理：将列表转换为集合提高查找效率
    prompt_ids_set = set(prompt_ids)
    corpus_ids_set = set(corpus_ids)
    
    # 预处理：构建prompt_id到特征向量的映射
    corpus_feature_map = {
        pf['id']: pf['vector'] 
        for pf in corpus_features 
        if pf['id'] in corpus_ids_set
    }
    
    # 预处理：构建(prompt_id, corpus_id)到accuracy的映射
    # 根据前端选择的攻击方式 检索特定攻击下的鲁棒性值
    result_map = {}
    
    if selected_attack_methods and len(selected_attack_methods) > 0:
        # 使用选择的攻击方式数据，从 final_results 中提取对应字段
        for res in final_results:
            if res['prompt_id'] in prompt_ids_set and res['corpus_id'] in corpus_ids_set:
                key = (res['prompt_id'], res['corpus_id'])
                attack_results = []
                
                # 提取选择的攻击方法的结果
                for method in selected_attack_methods:
                    field_name = f'prompt_{method}_result'
                    if field_name in res:
                        attack_results.append(res[field_name])
                
                # 如果有有效的攻击结果，计算平均值
                if attack_results:
                    avg_accuracy = sum(attack_results) / len(attack_results)
                    result_map[key] = avg_accuracy
    else:
        # 使用原始数据（所有攻击方式的平均）
        result_map = {
            (res['prompt_id'], res['corpus_id']): res['accuracy']
            for res in final_results 
            if res['prompt_id'] in prompt_ids_set and res['corpus_id'] in corpus_ids_set
        }
    
    # 结果字典，存储所有离散特征的鲁棒性值
    all_robustness = {}
    
    # 对每个离散特征计算鲁棒性
    for feature_name, feature_values in CORPUS_DISCRETE_FEATURES.items():
        dimension_index = CORPUS_FEATURE_DIMENSIONS[feature_name]
        feature_robustness = {}
        
        # 按特征值分组计算
        value_groups = defaultdict(list)
        for corpus_id, vector in corpus_feature_map.items():
            value = vector[dimension_index]
            if value in feature_values:  # 只处理预定义的特征值
                value_groups[value].append(corpus_id)
        
        # 对每个特征值计算鲁棒性
        for value, value_name in feature_values.items():
            matching_corpus_ids = value_groups.get(value, [])
            
            # 计算所有相关组合的accuracy
            accuracies = [
                result_map[(pid, cid)]
                for cid in matching_corpus_ids
                for pid in prompt_ids
                if (cid, pid) in result_map
            ]
            
            # 计算均值
            if accuracies:
                avg_accuracy = sum(accuracies) / len(accuracies)
                feature_robustness[value_name] = round(avg_accuracy, 2)
            else:
                feature_robustness[value_name] = None
        
        all_robustness[feature_name] = feature_robustness
    
    return all_robustness

# 加载数据函数
def load_data(file_path):
    """加载JSON文件内容"""
    try:
        if not os.path.exists(file_path):
            return []
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载文件失败: {e}")
        return []

# 数据缓存
prompt_data = load_data(PROMPT_FILE_PATH)
corpus_data = load_data(CORPUS_FILE_PATH)

# 根据ID获取prompt数据
@app.route('/get_prompt_data', methods=['POST'])
def get_prompt_data():
    try:
        data = request.json
        ids = data.get('ids', [])
        corpus_ids = data.get('corpus_ids', [])  # 新增：获取corpus_ids
        selected_attack_methods = data.get('selected_attack_methods', [])
        robustness_only = data.get('robustness_only', False)  # 新增：是否只计算鲁棒性
        print("进入get_prompt_data")
        print("prompt_ids数量", len(ids))
        print("corpus_ids数量", len(corpus_ids))
        print("选择的攻击方式", selected_attack_methods)
        print("仅计算鲁棒性模式:", robustness_only)
        
        # 统计每个 prompt_id 的 accuracy（只考虑筛选后的corpus_ids）
        # 根据前端选择的攻击方式 检索特定攻击下的鲁棒性值
        
        robustness_map = {}
        
        if selected_attack_methods and len(selected_attack_methods) > 0:
            # 使用选择的攻击方式数据，从 final_results 中提取对应字段
            for res in final_results:
                pid = res['prompt_id']
                cid = res['corpus_id']
                if pid in ids and cid in corpus_ids:
                    attack_results = []
                    
                    # 提取选择的攻击方法的结果
                    for method in selected_attack_methods:
                        field_name = f'prompt_{method}_result'
                        if field_name in res:
                            attack_results.append(res[field_name])
                    
                    # 如果有有效的攻击结果，计算平均值
                    if attack_results:
                        avg_accuracy = sum(attack_results) / len(attack_results)
                        robustness_map.setdefault(pid, []).append(avg_accuracy)
        else:
            # 使用原始数据
            for res in final_results:
                pid = res['prompt_id']
                cid = res['corpus_id']
                if pid in ids and cid in corpus_ids:  # 只考虑筛选后的组合
                    robustness_map.setdefault(pid, []).append(res['accuracy'])
        
        robustness_avg = {k: sum(v)/len(v) for k, v in robustness_map.items()}

        # 鲁棒性计算完成
        print("鲁棒性计算完成")

        # t-SNE降维（仅在非robustness_only模式下执行）
        xy_coords = {}
        if not robustness_only:
            # 获取嵌入向量
            embeddings = []
            valid_ids = []
            for pid in ids:
                emb = prompt_embedding_map.get(pid)
                if emb is not None:
                    embeddings.append(emb)
                    valid_ids.append(pid)
            print("嵌入向量获取完成")
            print("prompt_ids embeddings数量", len(embeddings))
            
            # 验证embeddings数据
            if len(embeddings) > 0:
                try:
                    embeddings_array = np.array(embeddings)
                    print("embeddings数组形状:", embeddings_array.shape)
                    print("embeddings数据类型:", embeddings_array.dtype)
                    print("embeddings是否包含NaN:", np.isnan(embeddings_array).any())
                    print("embeddings是否包含Inf:", np.isinf(embeddings_array).any())
                except Exception as e:
                    print("embeddings数据验证失败:", str(e))
            
            if len(embeddings) >= 3:
                try:
                    print("开始t-SNE降维，embeddings形状:", np.array(embeddings).shape)
                    # 动态调整perplexity，确保小于样本数量
                    n_samples = len(embeddings)
                    perplexity = min(30, max(5, n_samples // 3))  # 在5到30之间，且不超过样本数的1/3
                    print(f"使用perplexity: {perplexity}")
                    tsne = TSNE(n_components=2, random_state=42, perplexity=perplexity)
                    xy = tsne.fit_transform(np.array(embeddings))
                    print("t-SNE降维成功，结果形状:", xy.shape)
                    for i, pid in enumerate(valid_ids):
                        xy_coords[pid] = {'x': float(xy[i,0]), 'y': float(xy[i,1])}
                except Exception as tsne_error:
                    print("t-SNE降维失败:", str(tsne_error))
                    # 如果t-SNE失败，使用随机坐标
                    for pid in valid_ids:
                        xy_coords[pid] = {'x': None, 'y': None}
            else:
                print("prompt_ids embeddings数量小于3，无法进行t-SNE降维")
                for pid in valid_ids:
                    xy_coords[pid] = {'x': None, 'y': None}
            print("t-SNE降维完成")
        else:
            print("跳过t-SNE降维（仅计算鲁棒性模式）")
            # 在robustness_only模式下，为所有ID设置None坐标
            for pid in ids:
                xy_coords[pid] = {'x': None, 'y': None}
        result = []
        for item in prompt_data:
            if 'prompt_id' in item and item['prompt_id'] in ids:
                pid = item['prompt_id']
                coord = xy_coords.get(pid, {'x': None, 'y': None})
                
                # 获取特征向量信息
                features = {}
                for pf in prompt_features:
                    if pf['id'] == pid:
                        vector = pf['vector']
                        for i, value in enumerate(vector):
                            if i in PROMPT_FEATURE_NAMES:
                                feature_name = PROMPT_FEATURE_NAMES[i]
                                # 对于离散特征，尝试获取对应的文本描述
                                if feature_name in DISCRETE_FEATURES:
                                    discrete_values = DISCRETE_FEATURES[feature_name]
                                    if value in discrete_values:
                                        features[feature_name] = {
                                            'value': value,
                                            'description': discrete_values[value]
                                        }
                                    else:
                                        features[feature_name] = {
                                            'value': value,
                                            'description': f'未知值({value})'
                                        }
                                else:
                                    features[feature_name] = {
                                        'value': value,
                                        'description': f'连续值({value:.4f})'
                                    }
                        break
                
                result.append({
                    'id': pid,
                    'text': item['prompt'],
                    'robustness': round(robustness_avg.get(pid, 0), 3),
                    'x': coord['x'],
                    'y': coord['y'],
                    'features': features
                })
        print("结果获取完成")
        return jsonify({
            'success': True,
            'prompt': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'prompt': []
        }), 500

# 根据ID获取corpus数据
@app.route('/get_corpus_data', methods=['POST'])
def get_corpus_data():
    try:
        data = request.json
        ids = data.get('ids', [])
        prompt_ids = data.get('prompt_ids', [])  # 新增：获取prompt_ids
        selected_attack_methods = data.get('selected_attack_methods', [])
        robustness_only = data.get('robustness_only', False)  # 新增：是否只计算鲁棒性
        print("进入get_corpus_data")
        print("corpus_ids数量", len(ids))
        print("prompt_ids数量", len(prompt_ids))
        print("选择的攻击方式", selected_attack_methods)
        # 统计每个 corpus_id 的 accuracy（只考虑筛选后的prompt_ids）
        robustness_map = {}
        # 根据前端选择的攻击方式 检索特定攻击下的鲁棒性值

        if selected_attack_methods and len(selected_attack_methods) > 0:
            # 使用选择的攻击方式数据，从 final_results 中提取对应字段
            for res in final_results:
                cid = res['corpus_id']
                pid = res['prompt_id']
                if cid in ids and pid in prompt_ids:
                    attack_results = []
                    
                    # 提取选择的攻击方法的结果
                    for method in selected_attack_methods:
                        field_name = f'prompt_{method}_result'
                        if field_name in res:
                            attack_results.append(res[field_name])
                    
                    # 如果有有效的攻击结果，计算平均值
                    if attack_results:
                        avg_accuracy = sum(attack_results) / len(attack_results)
                        robustness_map.setdefault(cid, []).append(avg_accuracy)
        else:
            # 使用原始数据
            for res in final_results:
                cid = res['corpus_id']
                pid = res['prompt_id']
                if cid in ids and pid in prompt_ids:  # 只考虑筛选后的组合
                    robustness_map.setdefault(cid, []).append(res['accuracy'])
        
        robustness_avg = {k: sum(v)/len(v) for k, v in robustness_map.items()}
        print("鲁棒性计算完成")

        # 获取嵌入向量
        embeddings = []
        valid_ids = []
        for cid in ids:
            emb = corpus_embedding_map.get(cid)
            if emb is not None:
                embeddings.append(emb)
                valid_ids.append(cid)
        print("嵌入向量获取完成")
        print("embeddings数量", len(embeddings))
        
        # 验证embeddings数据
        if len(embeddings) > 0:
            try:
                embeddings_array = np.array(embeddings)
                print("corpus embeddings数组形状:", embeddings_array.shape)
                print("corpus embeddings数据类型:", embeddings_array.dtype)
                print("corpus embeddings是否包含NaN:", np.isnan(embeddings_array).any())
                print("corpus embeddings是否包含Inf:", np.isinf(embeddings_array).any())
            except Exception as e:
                print("corpus embeddings数据验证失败:", str(e))
        
        # t-SNE降维
        xy_coords = {}
        if robustness_only:
            print("仅计算鲁棒性模式，跳过corpus t-SNE降维")
            # 在仅计算鲁棒性模式下，坐标设为None
            for cid in valid_ids:
                xy_coords[cid] = {'x': None, 'y': None}
        elif len(embeddings) >= 3:
            try:
                print("开始corpus t-SNE降维，embeddings形状:", np.array(embeddings).shape)
                # 动态调整perplexity，确保小于样本数量
                n_samples = len(embeddings)
                perplexity = min(50, max(5, n_samples // 3))  # 在5到50之间，且不超过样本数的1/3
                print(f"corpus使用perplexity: {perplexity}")
                tsne = TSNE(n_components=2, random_state=42, perplexity=perplexity, learning_rate=400, early_exaggeration=20)
                xy = tsne.fit_transform(np.array(embeddings))
                print("corpus t-SNE降维成功，结果形状:", xy.shape)
                for i, cid in enumerate(valid_ids):
                    xy_coords[cid] = {'x': float(xy[i,0]), 'y': float(xy[i,1])}
            except Exception as tsne_error:
                print("corpus t-SNE降维失败:", str(tsne_error))
                # 如果t-SNE失败，使用随机坐标
                for cid in valid_ids:
                    xy_coords[cid] = {'x': None, 'y': None}
        else:
            print("embeddings数量小于3，无法进行t-SNE降维")
            for cid in valid_ids:
                xy_coords[cid] = {'x': None, 'y': None}
        print("t-SNE降维完成")
        result = []
        for item in corpus_data:
            if 'corpus_id' in item and item['corpus_id'] in ids:
                cid = item['corpus_id']
                coord = xy_coords.get(cid, {'x': None, 'y': None})
                
                # 获取特征向量信息
                features = {}
                for cf in corpus_features:
                    if cf['id'] == cid:
                        vector = cf['vector']
                        for i, value in enumerate(vector):
                            if i in CORPUS_FEATURE_NAMES:
                                feature_name = CORPUS_FEATURE_NAMES[i]
                                # 对于离散特征，尝试获取对应的文本描述
                                if feature_name in CORPUS_DISCRETE_FEATURES:
                                    discrete_values = CORPUS_DISCRETE_FEATURES[feature_name]
                                    if value in discrete_values:
                                        features[feature_name] = {
                                            'value': value,
                                            'description': discrete_values[value]
                                        }
                                    else:
                                        features[feature_name] = {
                                            'value': value,
                                            'description': f'未知值({value})'
                                        }
                                else:
                                    features[feature_name] = {
                                        'value': value,
                                        'description': f'连续值({value:.4f})'
                                    }
                        break
                
                result.append({
                    'id': cid,
                    'text': item['corpus'],
                    'robustness': round(robustness_avg.get(cid, 0), 3),
                    'x': coord['x'],
                    'y': coord['y'],
                    'features': features
                })
        print("结果获取完成")
        return jsonify({
            'success': True,
            'corpus': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'corpus': []
        }), 500

# 刷新数据
@app.route('/refresh_data', methods=['GET'])
def refresh_data():
    global prompt_data, corpus_data
    prompt_data = load_data(PROMPT_FILE_PATH)
    corpus_data = load_data(CORPUS_FILE_PATH)
    return jsonify({
        'success': True,
        'message': '数据已刷新'
    })


# @app.route('/get_feature_correlations', methods=['POST'])
# def get_feature_correlations():
#     """计算特征与鲁棒性的相关性"""
#     try:
#         data = request.get_json()
#         data_source_type = data.get('dataSourcetype', 'prompt')  # 默认处理prompt特征
#         prompt_ids = data.get('prompt_ids', [])
#         corpus_ids = data.get('corpus_ids', [])
        
#         # 数据校验
#         if not prompt_ids and not corpus_ids:
#             return jsonify({'success': False, 'error': '必须提供prompt_ids或corpus_ids'})
        
#         # 预处理ID列表
#         prompt_id_set = set(map(int, prompt_ids))
#         corpus_id_set = set(map(int, corpus_ids))
        
#         print(f"要处理的数据来源类型: {data_source_type}")
#         # 根据请求类型选择处理逻辑
#         if data_source_type == 'prompt':
#             return handle_prompt_features(prompt_id_set, corpus_id_set)
#         elif data_source_type == 'corpus':
#             return handle_corpus_features(prompt_id_set, corpus_id_set)
#         else:
#             return jsonify({'success': False, 'error': f'未知的dataSourceType: {data_source_type}'})
            
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'error': str(e),
#             # 'traceback': traceback.format_exc()
#         }), 500

# # def handle_prompt_features(prompt_id_set, corpus_id_set):
# #     """处理prompt特征相关性计算"""
# #     # 计算prompt的平均鲁棒性
# #     robustness_map = defaultdict(list)
# #     for res in final_results:
# #         if res['prompt_id'] in prompt_id_set and res['corpus_id'] in corpus_id_set:
# #             robustness_map[res['prompt_id']].append(res['accuracy'])
    
# #     prompt_robustness = {
# #         pid: np.mean(accuracies) if accuracies else None
# #         for pid, accuracies in robustness_map.items()
# #     }
    
# #     # 准备prompt特征数据
# #     prompt_features_filtered = [
# #         pf for pf in prompt_features 
# #         if pf['id'] in prompt_id_set
# #     ]
    
# #     # 计算prompt特征相关性
# #     prompt_results = calculate_feature_correlations(
# #         prompt_features_filtered, 
# #         prompt_robustness,
# #         DISCRETE_FEATURES,
# #         PROMPT_FEATURE_DIMENSIONS,
# #         CONTINUOUS_FEATURES
# #     )
    
# #     return jsonify({
# #         'success': True,
# #         'data_source_type': 'prompt',
# #         'correlations': prompt_results
# #     })

# # def handle_corpus_features(prompt_id_set, corpus_id_set):
# #     """处理corpus特征相关性计算"""
# #     # 计算corpus的平均鲁棒性
# #     robustness_map = defaultdict(list)
# #     for res in final_results:
# #         if res['prompt_id'] in prompt_id_set and res['corpus_id'] in corpus_id_set:
# #             robustness_map[res['corpus_id']].append(res['accuracy'])
    
# #     corpus_robustness = {
# #         cid: np.mean(accuracies) if accuracies else None
# #         for cid, accuracies in robustness_map.items()
# #     }
    
# #     # 准备corpus特征数据
# #     corpus_features_filtered = [
# #         cf for cf in corpus_features 
# #         if cf['id'] in corpus_id_set
# #     ]
    
# #     # 计算corpus特征相关性
# #     corpus_results = calculate_feature_correlations(
# #         corpus_features_filtered,
# #         corpus_robustness,
# #         CORPUS_DISCRETE_FEATURES,
# #         CORPUS_FEATURE_DIMENSIONS,
# #         CORPUS_CONTINUOUS_FEATURES
# #     )
    
# #     return jsonify({
# #         'success': True,
# #         'data_source_type': 'corpus',
# #         'correlations': corpus_results
# #     })

# # def calculate_feature_correlations(features, robustness_map, discrete_feats, discrete_dims, continuous_feats):
#     """通用特征相关性计算函数"""
#     results = {'discrete': {}, 'continuous': {}}
    
#     # 离散特征计算
#     for feat_name, value_map in discrete_feats.items():
#         feat_idx = discrete_dims[feat_name]
#         groups = defaultdict(list)
        
#         for feat in features:
#             if feat['id'] in robustness_map:
#                 value = feat['vector'][feat_idx]
#                 if value in value_map:
#                     groups[value].append(robustness_map[feat['id']])
        
#         # 计算ANOVA
#         if len(groups) >= 2:
#             f_val, p_val = stats.f_oneway(*[np.array(x) for x in groups.values()])
#             eta_sq = f_val / (f_val + (len(features) - len(groups)))
#             results['discrete'][feat_name] = {
#                 'effect_size': eta_sq,
#                 'p_value': p_val,
#                 'method': 'ANOVA'
#             }
    
#     # 连续特征计算
#     for feat_name, config in continuous_feats.items():
#         feat_idx = config['index']
#         x = []
#         y = []
        
#         for feat in features:
#             if feat['id'] in robustness_map:
#                 x_val = feat['vector'][feat_idx]
#                 if not np.isnan(x_val):
#                     x.append(x_val)
#                     y.append(robustness_map[feat['id']])
        
#         if len(x) >= 2:
#             # 计算Spearman
#             rho, p_val = stats.spearmanr(x, y)
#             results['continuous'][feat_name] = {
#                 'correlation': rho,
#                 'p_value': p_val,
#                 'method': 'Spearman'
#             }
    
#     return results

@app.route('/api/filter_by_features', methods=['POST'])
def filter_by_features():
    try:
        data = request.get_json()
        selected_features = data.get('selectedFeatures', {})
        data_source = data.get('dataSource', 'prompt')  # 'prompt' 或 'corpus'
        print(f"筛选的数据来源: {data_source}")
        print(f"筛选的特征: {selected_features}")
        
        # 获取所有ID
        all_ids = set()
        if data_source == 'prompt':
            all_ids = {pf['id'] for pf in prompt_features}
            feature_dimensions = PROMPT_FEATURE_DIMENSIONS
            continuous_features = CONTINUOUS_FEATURES
            feature_data = prompt_features
        else:
            all_ids = {cf['id'] for cf in corpus_features}
            feature_dimensions = CORPUS_FEATURE_DIMENSIONS
            continuous_features = CORPUS_CONTINUOUS_FEATURES
            feature_data = corpus_features
        
        # 存储每个特征的匹配ID集合
        feature_matches = defaultdict(set)
        
        # 遍历每个选择的条件
        for feature in selected_features:
            feature_name = feature['featureName']
            value_range = feature['valueRange']
            is_continuous = feature['isContinuous']
            
            # 获取特征索引
            if is_continuous:
                feature_index = continuous_features[feature_name]['index']
            else:
                feature_index = feature_dimensions[feature_name]
            
            print(f"\n处理特征 {feature_name}, 维度索引: {feature_index}")
            
            # 处理连续特征
            if is_continuous:
                min_val, max_val = map(float, value_range.split('-'))
                matching_ids = set()
                for item in feature_data:
                    feature_value = item['vector'][feature_index]
                    if min_val <= feature_value < max_val:
                        matching_ids.add(item['id'])
                print(f"连续特征 {feature_name} 在范围 {value_range} 内找到 {len(matching_ids)} 个匹配项")
                if len(matching_ids) > 0:
                    print(f"匹配的ID示例: {sorted(list(matching_ids))[:5]}")  # 只显示前5个ID
            # 处理离散特征
            else:
                # 获取特征值映射
                if data_source == 'prompt':
                    value_map = DISCRETE_FEATURES[feature_name]
                else:
                    value_map = CORPUS_DISCRETE_FEATURES[feature_name]
                
                # 将文本描述映射到数值
                value = None
                for num, text in value_map.items():
                    if text == value_range:
                        value = num
                        break
                
                if value is None:
                    print(f"警告：特征 {feature_name} 的值 {value_range} 没有找到对应的数值映射")
                    continue
                
                matching_ids = set()
                for item in feature_data:
                    if item['vector'][feature_index] == value:
                        matching_ids.add(item['id'])
                print(f"离散特征 {feature_name} 值 {value_range} (数值: {value}) 找到 {len(matching_ids)} 个匹配项")
                if len(matching_ids) > 0:
                    print(f"匹配的ID示例: {sorted(list(matching_ids))[:5]}")  # 只显示前5个ID
            
            # 存储这个特征的匹配结果（使用集合的并集）
            feature_matches[feature_name].update(matching_ids)
        
        # 计算所有特征的交集
        if feature_matches:
            filtered_ids = set.intersection(*feature_matches.values())
            print(f"\n所有特征的交集结果:")
            print(f"最终筛选出的ID数量: {len(filtered_ids)}")
            if filtered_ids:
                print(f"筛选出的ID: {sorted(list(filtered_ids))}")
        else:
            # 没有特征时，返回所有id（0~659）
            filtered_ids = set(range(660))
            print("没有提供任何特征条件，返回所有ID 0~659")
        
        # 转换为列表并排序
        result_ids = sorted(list(filtered_ids))
        
        return jsonify({
            'success': True,
            'filtered_ids': result_ids
        })
        
    except Exception as e:
        print(f"筛选过程出错: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)