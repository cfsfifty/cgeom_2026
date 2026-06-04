import FileObj3d
import copy
from dataclasses import dataclass
from BinaryNode  import BinaryNode
from typing import Optional 

@dataclass
class ProgramState:
	model : FileObj3d.FileObj3d
	node  : Optional[BinaryNode]

	level      : int
	max_level  : int

	cam_dir    : tuple[float]
	start_dir  : tuple[float]
	cam_scale  : float
	inter_x    : int
	inter_y    : int
	inter_type : int

	def __init__(self, cam_dir):
		self.model = FileObj3d.FileObj3d()
		self.node  = None

		self.level = 0
		self.max_level = 0

		self.cam_dir   = cam_dir
		self.start_dir = copy.deepcopy(cam_dir)
		self.cam_scale = 1.0
		self.inter_x = 0
		self.inter_y = 0
		self.inter_type = -1

	def __str__ (self):
		return str(self.node) + " at level " + str(self.level)
	

