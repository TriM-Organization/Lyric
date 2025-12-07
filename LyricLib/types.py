
# -*- coding: utf-8 -*-

"""
类型定义
"""

"""
版权所有 © 2025 金羿ELS
Copyright © 2025 Eilles

开源相关声明请见 仓库根目录下的 License.md
Terms & Conditions: License.md in the root directory
"""

# 睿乐组织 开发交流群 861684859
# Email TriM-Organization@hotmail.com
# 若需转载或借鉴 许可声明请查看仓库目录下的 License.md



from typing import Protocol, runtime_checkable

@runtime_checkable
class CopyableSequence(Protocol):
    def __len__(self) -> int: ...
    def __getitem__(self, i): ...
    def copy(self): ...