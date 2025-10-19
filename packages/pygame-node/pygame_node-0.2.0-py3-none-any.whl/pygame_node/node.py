import math
from collections import defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Tuple, List, Dict

import pygame
from pygame import Rect, Vector3, Surface, Mask
import numpy as np

from pygame_node import MouseButton
from pygame_node.data.node import Size
from pygame_node.data.font import Font
from pygame_node.attribute.style import Style, TextStyle
from pygame_node.data.event import PointerDownEvent, PointerUpEvent, PointerMoveEvent
from pygame_node.event import EventHandler


class Node:
    font: Font = None

    def __init__(self,
                 name: str,                                 # 名字
                 parent: 'Node' = None,                     # 父对象
                 *,                                         # 后面必须位置传参
                 position: Vector3 = None,                  # 坐标
                 visible: bool = True,                      # 是否显示
                 rotation: float = 0.0,                     # 旋转
                 size: Size = None,                         # 大小
                 style: Style = None) -> None:
        self._name = name
        self._parent = parent
        self._style = style or Style()
        self.children: List['Node'] = []
        self._visible = visible
        self._rotation = rotation
        self._size = Size(*(size if size is not None else (-1, -1)))
        self._position = position or Vector3(0, 0, 0)
        self._event = EventHandler()
        self._surface: Surface = Surface((0, 0), pygame.SRCALPHA)
        self.__style__ = deepcopy(self.style)
        self.rect
        # self._surface = Surface((self.width, self.height), pygame.SRCALPHA)

    @property
    def name(self) -> str:
        """获取名字"""
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

    @property
    def parent(self) -> 'Node':
        """获取父节点"""
        return self._parent

    @parent.setter
    def parent(self, parent: 'Node'):
        self._parent = parent
        parent.children.append(self)

    @property
    def style(self) -> Style:
        """获取样式"""
        return self._style

    @style.setter
    def style(self, style: Style):
        self._style = style
        self.reload_render()

    @property
    def size(self) -> Size:
        """获取大小"""
        return self._size

    @size.setter
    def size(self, value) -> None:
        if isinstance(value, (tuple, Size)):
            self._size = Size(*value)
        else:
            raise ValueError("Size")
        self.reload_render()

    @property
    def rect(self) -> Rect:
        """获取矩形区域"""
        return Rect(self._position.xy, (self.size.width, self.size.height))

    @property
    def x(self) -> int:
        """获取 x 坐标"""
        return self._position.x

    @x.setter
    def x(self, x: int):
        offset = x - self.x
        for child in self.children:
            child.x += offset
        self._position.x = x

    @property
    def y(self) -> int:
        """获取 y 坐标"""
        return self._position.y

    @y.setter
    def y(self, y: int):
        offset = y - self.y
        for child in self.children:
            child.y += offset
        self._position.y = y

    @property
    def width(self) -> int:
        """获取宽"""
        return self.size.width

    @property
    def height(self) -> int:
        """获取高"""
        return self.size.height

    @property
    def visible(self) -> bool:
        """是否显示"""
        return self._visible

    @visible.setter
    def visible(self, value) -> bool:
        """是否显示"""
        self._visible = bool(value)

    @property
    def rotation(self) -> float:
        """获取旋转角度"""
        return self._rotation % 360

    @rotation.setter
    def rotation(self, rotation: float):
        self._rotation = rotation
        self.reload_render()

    @property
    def surface(self) -> Surface:
        """获取区域"""
        return self._surface

    @property
    def mask(self):
        """获取实际内容区域"""
        return pygame.mask.from_surface(self.surface)

    @property
    def event(self) -> EventHandler:
        return self._event

    def draw(self, scene: Surface) -> None:
        if not self.visible:
            return
        if self.style.background.color is not None:
            res = Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(res, self.style.background.color.rgba, (0, 0, self.width, self.height),
                             border_radius=self.style.background.border_radius)
            scene.blit(res, (self.x, self.y))

    def update(self, dt: float) -> None:
        """更新状态"""
        for _node in self.children:
            _node.update(dt)

    def reload_render(self) -> None:
        """刷新渲染缓存"""

class Text(Node):
    """文本"""

    def __init__(self,
                 text: str,                 # 文本
                 font: Font = None,         # 字体
                 antialias: bool = False,   # 抗锯齿
                 name: str = None,
                 parent: 'Node' = None,
                 *,
                 copy_font: bool = True,
                 position: Vector3 = Vector3(0, 0, 0),
                 visible: bool = True,
                 rotation: float = 0.0,
                 size: Size = None,
                 style: Style = None):
        super().__init__(name or "TextNode", parent, position=position, visible=visible, rotation=rotation, size=size, style=style or TextStyle())
        self._rect = None
        self._text = text
        if copy_font:
            self._font = deepcopy(font or Node.font)
        else:
            self._font = font or Node.font
        self.__font__ = deepcopy(self._font)
        self._antialias = antialias
        self.reload_render()

    @property
    def text(self) -> str:
        """获取文本"""
        return self._text

    @text.setter
    def text(self, text: str):
        self._text = text
        self.reload_render()

    @property
    def font(self) -> Font:
        """获取字体"""
        return self._font

    @font.setter
    def font(self, font: Font):
        self._font = font
        self.reload_render()

    @property
    def style(self) -> TextStyle: return Node.style.fget(self)

    @property
    def antialias(self) -> bool:
        """获取抗锯齿"""
        return self._antialias

    @antialias.setter
    def antialias(self, antialias: bool) -> None:
        self._antialias = antialias
        self.reload_render()

    @property
    def render(self) -> Surface:
        """获取渲染"""
        return self._surface

    @property
    def mask(self) -> Mask:
        return pygame.mask.from_surface(self.render)

    @property
    def size(self) -> Size:
        return Size(*self.render.get_size())

    def draw(self, scene: Surface) -> None:
        super().draw(scene)
        if self.__style__ != self.style or self.__font__ != self.font:
            self.reload_render()
        scene.blit(self.render, (self.x, self.y))

    def text_stroke(self, text_surface: Surface) -> Surface:
        """绘制带描边的文本"""
        stroke_size = self.style.stroke.size

        # 计算描边需要扩展的空间
        stroke_width = text_surface.get_width() + 2 * stroke_size
        stroke_height = text_surface.get_height() + 2 * stroke_size
        stroke_surface = pygame.Surface((stroke_width, stroke_height), pygame.SRCALPHA)

        # 在8个方向上绘制描边颜色
        offsets = [(-1, -1), (0, -1), (1, -1),
                   (-1,  0),          (1,  0),
                   (-1,  1), (0,  1), (1,  1)]

        for ox, oy in offsets:
            offset_x = stroke_size + ox * stroke_size
            offset_y = stroke_size + oy * stroke_size
            # 绘制描边颜色
            stroke_surface.blit(text_surface, (offset_x, offset_y))

        # 用描边颜色填充所有绘制过的区域
        for x in range(self.size.width):
            for y in range(self.size.height):
                if stroke_surface.get_at((x, y))[3] > 0:  # 如果有像素存在
                    stroke_surface.set_at((x, y), self.style.stroke.color.rgb)

        # 在描边Surface上绘制原始文本（覆盖中心部分）
        stroke_surface.blit(text_surface, (stroke_size, stroke_size))

        # 将带描边的文本绘制到场景
        return stroke_surface

    def text_shadow(self, text_surface: Surface) -> Surface:
        """绘制带阴影和旋转的文本，返回拼接后的Surface"""
        angle_rad = math.radians(self.style.shadow.angle)
        shadow_offset_x = self.style.shadow.distance * math.cos(angle_rad)
        shadow_offset_y = self.style.shadow.distance * math.sin(angle_rad)

        shadow_surf = Surface(text_surface.get_size(), pygame.SRCALPHA)
        shadow_surf.fill((*self.style.shadow.color.rgb, int(255 * self.style.shadow.opacity)))

        text_surface_alpha = text_surface.copy().convert_alpha()
        shadow_surf.blit(text_surface_alpha, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        shadow_x = self.x + int(shadow_offset_x)
        shadow_y = self.y + int(shadow_offset_y)

        # 计算文本和阴影的边界矩形
        text_bound = text_surface.get_rect(topleft=(self.x, self.y))
        shadow_bound = shadow_surf.get_rect(topleft=(shadow_x, shadow_y))

        # 计算能同时包含文本和阴影的最小矩形
        bounding_rect = text_bound.union(shadow_bound)

        # 创建新的Surface（支持透明通道）
        combined_surface = Surface(bounding_rect.size, pygame.SRCALPHA)
        combined_surface.fill((0, 0, 0, 0))  # 填充透明背景

        # 先绘制阴影（在底层）
        shadow_pos = (shadow_bound.x - bounding_rect.x, shadow_bound.y - bounding_rect.y)
        combined_surface.blit(shadow_surf, shadow_pos)

        # 再绘制文本（在顶层）
        text_pos = (text_bound.x - bounding_rect.x, text_bound.y - bounding_rect.y)
        combined_surface.blit(text_surface, text_pos)

        return combined_surface

    def reload_render(self) -> None:
        # 处理换行符：按行分割文本
        lines = self.text.split('\n')

        # 计算文本总高度（行数 × 行高）
        line_height = self.font.get_sized_height(self.font.size)  # 获取字体高度
        total_height = len(lines) * line_height

        # 计算最大宽度
        max_width = 0
        line_surfaces = []

        for line in lines:
            if line:  # 非空行
                line_surface, line_rect = self.font.render(
                    line,
                    fgcolor=self.style.color.rgb,
                    size=self.font.size
                )
                max_width = max(max_width, line_rect.width)
                line_surfaces.append(line_surface)
            else:
                # 空行也保留位置
                line_surfaces.append(pygame.Surface((0, line_height), pygame.SRCALPHA))

        # 创建总Surface容纳所有行
        text_surface = pygame.Surface((max_width, total_height), pygame.SRCALPHA)
        text_surface.fill((0, 0, 0, 0))  # 透明背景

        # 逐行渲染到总Surface
        y_offset = 0
        for line_surface in line_surfaces:
            if line_surface.get_size() != (0, 0):  # 非空行
                text_surface.blit(line_surface, (0, y_offset))
            y_offset += line_height

        # 后续处理保持不变
        if self.rotation != 0:
            text_surface = pygame.transform.rotozoom(text_surface, self.rotation, 1.0)

        self.__style__ = deepcopy(self.style)

        if self.__style__.stroke.enable:
            text_surface = self.text_stroke(text_surface)
        if self.__style__.shadow.enable:
            text_surface = self.text_shadow(text_surface)

        self._surface = text_surface

class TextButton(Text):
    """文本按钮"""

    def __init__(self,
                 text: str,
                 font: Font = None,
                 antialias: bool = False,
                 name: str = None,
                 parent: 'Node' = None,
                 *,
                 position: Vector3 = Vector3(0, 0, 0),
                 visible: bool = True,
                 rotation: float = 0.0,
                 size: Size = None,
                 style: Style = TextStyle()):
        super().__init__(text, font, antialias, name, parent, position=position, visible=visible, rotation=rotation,
                         size=size, style=style)

        self.event(self.on_click)
        self.event(self.up_click)

    def on_click(self, event: PointerDownEvent):
        """被鼠标按下时修改样式"""
        if (event.button_index == MouseButton.MOUSE_BUTTON_WHEEL_UP or
                event.button_index == MouseButton.MOUSE_BUTTON_WHEEL_UP): return
        self.style.color.r *= 1.2
        self.style.color.g *= 1.2
        self.style.color.b *= 1.2

    def up_click(self, event: PointerUpEvent):
        """鼠标松开时恢复样式"""
        if (event.button_index == MouseButton.MOUSE_BUTTON_WHEEL_UP or
                event.button_index == MouseButton.MOUSE_BUTTON_WHEEL_UP): return
        self.style.color.r /= 1.2
        self.style.color.g /= 1.2
        self.style.color.b /= 1.2

class Sprite2D(Node):
    """2D 精灵"""

    def __init__(self,
                 image: Surface | Path | str,
                 name: str = None,
                 parent: 'Node' = None,
                 *,
                 position: Vector3 = Vector3(0, 0, 0),
                 visible: bool = True,
                 rotation: float = 0.0,
                 size: Size = None,
                 style: Style = None):
        super().__init__(name, parent, position=position, visible=visible, rotation=rotation,
                             size=size, style=style)
        if isinstance(image, Surface):
            self._image = image
        elif isinstance(image, (Path, str)):
            self._image = pygame.image.load(str(Path(image))).convert_alpha()
        else:
            raise ValueError("Image")
        self.reload_render()

    @property
    def image(self) -> Surface:
        return self._image

    def draw(self, scene: Surface) -> None:
        super().draw(scene)
        if self.__style__ != self.style:
            self.reload_render()
        scene.blit(self.surface, (self.x, self.y))

    def reload_render(self) -> None:
        if not (self.size.width < 0 and self.size.height < 0):
            self._surface = pygame.transform.scale(self.image, (*self.size,))
        else:
            self._surface = self.image
            self._size = Size(*self.image.get_size())
        self.__style__ = self.style

class TextureButton(Sprite2D):
    """精灵按钮"""

    def __init__(self,
                 image: Surface | Path | str,
                 name: str = None,
                 parent: 'Node' = None,
                 *,
                 position: Vector3 = Vector3(0, 0, 0),
                 visible: bool = True,
                 rotation: float = 0.0,
                 size: Size = None,
                 style: Style = TextStyle()):
        super().__init__(image, name, parent, position=position, visible=visible, rotation=rotation,
                         size=size, style=style)
        self.default_su = self.surface
        self.chick = self.pixel_operations(1.1, lambda x, y: x * y)

        self.event(self.on_click)
        self.event(self.up_click)

    def on_click(self, event: PointerDownEvent):
        """被鼠标按下时修改样式"""
        if (event.button_index == MouseButton.MOUSE_BUTTON_WHEEL_UP or
                event.button_index == MouseButton.MOUSE_BUTTON_WHEEL_UP): return
        self._surface = self.chick

    def up_click(self, event: PointerUpEvent):
        """鼠标松开时恢复样式"""
        if (event.button_index == MouseButton.MOUSE_BUTTON_WHEEL_UP or
                event.button_index == MouseButton.MOUSE_BUTTON_WHEEL_UP): return
        self._surface = self.default_su


    def pixel_operations(self, coefficient: float, op_func) -> pygame.Surface:
        """对图像做操作"""
        rgb_array = pygame.surfarray.array3d(self.surface)  # 3D数组 (width, height, 3)
        alpha_array = pygame.surfarray.array_alpha(self.surface)  # 2D数组 (width, height)

        rgb_float = rgb_array.astype(np.float32)
        rgb_float = op_func(rgb_float, coefficient)
        rgb_processed = np.clip(rgb_float, 0, 255).astype(np.uint8)

        result_surface = pygame.Surface(self.surface.get_size(), pygame.SRCALPHA, 32)

        result_rgb = pygame.surfarray.pixels3d(result_surface)  # RGB通道
        result_alpha = pygame.surfarray.pixels_alpha(result_surface)  # Alpha通道

        result_rgb[:, :, :] = rgb_processed

        result_alpha[:, :] = alpha_array

        del result_rgb
        del result_alpha

        return result_surface

    def reload_render(self) -> None:
        super().reload_render()
        self.default_su = self.surface
        self.chick = self.pixel_operations(1.1, lambda x, y: x * y)

class Tile(Sprite2D):
    """瓦片"""

    def __init__(self, image: Surface | Path | str, **kwargs):
        super().__init__(image)
        for key, value in kwargs.items():
            setattr(self, key, value)

class TileMapLayer(Node):
    """
    瓦片地图图层
    """

    def __init__(self,
                 tilemap: Surface | Path | str,
                 tile_size: Size,
                 name: str = None,
                 parent: 'Node' = None,
                 *,
                 position: Vector3 = Vector3(0, 0, 0),
                 visible: bool = True,
                 rotation: float = 0.0,
                 size: Size = None,
                 style: Style = None):
        super().__init__(name, parent, position=position, visible=visible, rotation=rotation,
                             size=size, style=style)
        if isinstance(tilemap, Surface):
            self._tilemap = tilemap
        elif isinstance(tilemap, (Path, str)):
            self._tilemap = pygame.image.load(str(Path(tilemap)))
        else:
            raise ValueError("Tilemap")
        self._tilesize = Size(*tile_size)
        self.tiles: List[Tile] = []
        self.map: Dict[int, Dict[int, Dict[int, Dict]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
        for y in range(0, self.tilemap.get_height(), tile_size[1]):
            for x in range(0, self.tilemap.get_width(), tile_size[0]):
                self.tiles.append(Tile(self.tilemap.subsurface((x, y, tile_size[0], tile_size[1]))))

    @property
    def tilemap(self) -> Surface:
        """返回瓦砖"""
        return self._tilemap

    @property
    def tilesize(self) -> Size:
        """返回瓦片大小"""
        return self._tilesize

    def __getitem__(self, item) -> Tile:
        return self.tiles[item]

    def __len__(self) -> int:
        return len(self.tiles)

    def set_cell(self, pos: Vector3, cell_id: int) -> None:
        """
        添加瓦片
        :param pos: 瓦片位置
        :param cell_id: 瓦片id
        :return:
        """
        pos = Vector3(pos)
        self.map[pos.x][pos.y][pos.z] = cell_id

    def draw(self, scene: Surface) -> None:
        for x, _xdata in self.map.items():
            for y, _ydata in _xdata.items():
                for z, cell_id in {k: _ydata[k] for k in sorted(_ydata.keys())}.items():
                    scene.blit(self.tiles[cell_id].surface, (self.x + x * self.tilesize.width, self.y + y * self.tilesize.height))
