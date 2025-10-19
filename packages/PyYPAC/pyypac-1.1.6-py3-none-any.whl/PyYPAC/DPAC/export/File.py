from io import BytesIO
from typing import BinaryIO
import math


class File:
	def __init__(self, indict: dict, out_path: str):
		with open(out_path, 'wb', buffering=2048 * 7) as out:
			self.write(indict, out)

	def _pad(self, x: int, align: int) -> int:
		return (align - (x & (align - 1))) & (align - 1)

	def write(self, indict: dict, out: BinaryIO):
		data = BytesIO()
		toc = BytesIO()
		header = BytesIO()

		for key, value in indict.items():
			if key == 'id':
				if not isinstance(value, str):
					raise TypeError("Expected string for 'id'")
				assert len(value) <= 4
				header.write(value.encode('shift_jis'))

			elif key == 'table':
				if not isinstance(value, dict):
					raise TypeError("Expected dict for 'table'")
				for folder, records in value.items():
					assert len(folder) <= 4
					toc.write(folder.encode('shift_jis'))

					# Write the folder size ONCE
					size = ((math.ceil((len(records) & 4095) / 3) * 3)).to_bytes(2, byteorder='little')
					toc.write(size)
					toc.write(b'\x00\x00')

					for key2, value2 in records.items():
						if key2 == 'name':
							toc.write(value2.ljust(4).encode('shift_jis'))

						elif key2 == 'path':
							with open(value2, 'rb') as f:
								offset = data.tell()
								payload = f.read()

								count = self._pad(len(payload), 256)
								payload += b'\x00' * count
								data.write(payload)

								file_size = (len(payload) // 256).to_bytes(2, 'little')
								count = self._pad(data.tell(), 2048)
								data.write(b'\x00' * count)

								sector = (offset // 2048).to_bytes(2, byteorder='little')
								toc.write(sector)
								toc.write(file_size)


		# Write header
		out.write(header.getvalue())

		# Write TOC and data sizes
		out.write(len(toc.getvalue()).to_bytes(4, byteorder='little'))
		out.write(len(data.getvalue()).to_bytes(4, byteorder='little'))

		# Write whatever this control word is supposed to be
		out.write(b'\x07\x00\x00\x00')

		# Pad to 2048-byte boundary
		count = self._pad(out.tell(), 2048)
		out.write(b'\x00' * count)

		# Write TOC
		out.write(toc.getvalue())

		# Align to 0x4000 boundary
		ALIGN = 0x4000
		padding = (-out.tell()) % ALIGN
		out.write(b'\x00' * padding)

		# Finally write data section
		out.write(data.getvalue())