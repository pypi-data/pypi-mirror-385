from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from omegaconf import OmegaConf
import torch

import nndesigner
import nndesigner.system_op
import os

DEFAULT_CONFIG_DIR = os.path.join(os.path.dirname(nndesigner.__file__), "config")
DEFAULT_NODE_GROUP_CONFIG_PATH = os.path.join(DEFAULT_CONFIG_DIR, "system/node_groups.json")


def get_node_params(cls):
	"""
	获取类的 __init__ 参数及默认值，以及 forward 方法的参数和返回值类型与数量
	:param cls: 传入的类对象（如 torch.nn.Linear）
	:return: dict，包含 init_args, forward_args, forward_return, forward_return_count
	"""
	import inspect, typing
	result = {}

	# 获取 __init__ 参数和默认值
	try:
		init_sig = inspect.signature(cls.__init__)
		init_args = []
		for name, param in init_sig.parameters.items():
			if name == 'self':
				continue
			arg_info = {'name': name}
			# 类型注解
			if param.annotation is not inspect.Parameter.empty:
				if hasattr(param.annotation, '__name__'):
					arg_info['type'] = param.annotation.__name__
				else:
					arg_info['type'] = str(param.annotation)
			else:
				arg_info['type'] = None
			if param.default is not inspect.Parameter.empty:
				arg_info['default'] = param.default
			else:
				arg_info['default'] = None
			init_args.append(arg_info)
		result['init_args'] = init_args
	except Exception:
		result['init_args'] = []

	# 获取 forward 参数和返回值
	forward = getattr(cls, 'forward', None)
	if forward:
		try:
			forward_sig = inspect.signature(forward)
			forward_args = []
			for name, param in forward_sig.parameters.items():
				if name == 'self':
					continue
				arg_info = {'name': name}
				# 类型注解
				if param.annotation is not inspect.Parameter.empty:
					if hasattr(param.annotation, '__name__'):
						arg_info['type'] = param.annotation.__name__
					else:
						arg_info['type'] = str(param.annotation)
				else:
					arg_info['type'] = None
				if param.default is not inspect.Parameter.empty:
					arg_info['default'] = param.default
				else:
					arg_info['default'] = None
				forward_args.append(arg_info)
			result['forward_args'] = forward_args

			# 返回值类型和数量
			ann = forward_sig.return_annotation
			if ann is not inspect.Signature.empty:
				origin = getattr(ann, '__origin__', None)
				args = getattr(ann, '__args__', None)
				if origin is tuple or origin is typing.Tuple:
					result['forward_return'] = 'Tuple'
					result['forward_return_count'] = len(args) if args else 0
				else:
					result['forward_return'] = ann.__name__ if hasattr(ann, '__name__') else str(ann)
					result['forward_return_count'] = 1
			else:
				result['forward_return'] = None
				result['forward_return_count'] = 0
		except Exception:
			result['forward_args'] = []
			result['forward_return'] = None
			result['forward_return_count'] = 0
	else:
		result['forward_args'] = []
		result['forward_return'] = None
		result['forward_return_count'] = 0

	return result