"""
MCP集成模块
提供与现有系统的MCP链接支持
"""


class MCPServer:
    """MCP服务器集成类"""

    def __init__(self):
        self.tools = {}

    def register_tool(self, name: str, func, description: str):
        """注册MCP工具"""
        self.tools[name] = {
            'function': func,
            'description': description
        }

    def get_tools(self) -> list:
        """获取所有工具定义"""
        return [
            {
                'name': name,
                'description': info['description'],
                'parameters': {}
            }
            for name, info in self.tools.items()
        ]


# MCP工具定义
MCP_TOOLS = {
    'ulanzi_get_unreviewed': {
        'description': '获取待审核的分类结果',
        'parameters': {
            'limit': {'type': 'number', 'description': '返回数量限制'},
            'job_id': {'type': 'number', 'description': '任务ID'},
            'min_score': {'type': 'number', 'description': '最低得分'}
        }
    },
    'ulanzi_submit_review': {
        'description': '提交审核修正结果',
        'parameters': {
            'result_id': {'type': 'number', 'description': '结果ID'},
            'corrected_category': {'type': 'string', 'description': '修正分类'},
            'auditor': {'type': 'string', 'description': '审核人'}
        }
    },
    'ulanzi_get_rules': {
        'description': '获取当前生效的分类规则',
        'parameters': {}
    },
    'ulanzi_test_classification': {
        'description': '测试单个商品标题的分类',
        'parameters': {
            'sku_title': {'type': 'string', 'description': '商品标题'},
            'site': {'type': 'string', 'description': '站点(JP/US/CN)'}
        }
    },
    'ulanzi_batch_classify': {
        'description': '批量分类商品标题',
        'parameters': {
            'titles': {'type': 'array', 'description': '商品标题列表'},
            'site': {'type': 'string', 'description': '站点代码'}
        }
    }
}


def create_mcp_tools(classification_service, database_manager=None):
    """
    创建MCP工具函数

    Args:
        classification_service: 分类服务实例
        database_manager: 数据库管理器实例（可选）

    Returns:
        工具函数字典
    """
    tools = {}

    def get_unreviewed(limit=50, job_id=None, min_score=0):
        """获取待审核的分类结果"""
        if database_manager is None:
            return {'error': '数据库管理器未初始化'}
        try:
            df = database_manager.get_unreviewed_results(job_id, limit)
            return {
                'count': len(df),
                'results': df.to_dict('records')
            }
        except Exception as e:
            return {'error': str(e)}

    tools['ulanzi_get_unreviewed'] = {
        'function': get_unreviewed,
        'description': MCP_TOOLS['ulanzi_get_unreviewed']['description']
    }

    def submit_review(result_id, corrected_category, auditor='system'):
        """提交审核修正结果"""
        if database_manager is None:
            return {'error': '数据库管理器未初始化'}
        try:
            database_manager.update_result_audit(result_id, corrected_category, auditor)
            return {'success': True, 'result_id': result_id}
        except Exception as e:
            return {'error': str(e)}

    tools['ulanzi_submit_review'] = {
        'function': submit_review,
        'description': MCP_TOOLS['ulanzi_submit_review']['description']
    }

    def get_rules():
        """获取当前生效的分类规则"""
        from .rules_loader import RulesLoader
        try:
            loader = RulesLoader()
            rules_summary = loader.get_rules_summary()
            categories = {}
            for cat in loader.get_all_categories():
                info = loader.get_category_info(cat)
                categories[cat] = {
                    'base_score': info['base_score'],
                    'positive_weights': info['positive_weights'],
                    'negative_weights': info['negative_weights']
                }
            return {
                'summary': rules_summary,
                'categories': categories
            }
        except Exception as e:
            return {'error': str(e)}

    tools['ulanzi_get_rules'] = {
        'function': get_rules,
        'description': MCP_TOOLS['ulanzi_get_rules']['description']
    }

    def test_classification(sku_title, site='JP'):
        """测试单个商品标题的分类"""
        try:
            result = classification_service.classify(sku_title, site)
            return {
                'original_title': result['original_title'],
                'clean_title': result['clean_title'],
                'predicted_category': result['predicted_category'],
                'decision_reason': result['decision_reason'],
                'scores_all': result['scores_all'],
                'score_ranking': result['score_ranking']
            }
        except Exception as e:
            return {'error': str(e)}

    tools['ulanzi_test_classification'] = {
        'function': test_classification,
        'description': MCP_TOOLS['ulanzi_test_classification']['description']
    }

    def batch_classify(titles, site='JP'):
        """批量分类商品标题"""
        try:
            results = []
            for title in titles:
                result = classification_service.classify(title, site)
                results.append({
                    'title': title,
                    'predicted_category': result['predicted_category'],
                    'decision_reason': result['decision_reason'],
                    'max_score': result['scores_all'].get(result['predicted_category'], 0)
                })
            return {'count': len(results), 'results': results}
        except Exception as e:
            return {'error': str(e)}

    tools['ulanzi_batch_classify'] = {
        'function': batch_classify,
        'description': MCP_TOOLS['ulanzi_batch_classify']['description']
    }

    return tools
