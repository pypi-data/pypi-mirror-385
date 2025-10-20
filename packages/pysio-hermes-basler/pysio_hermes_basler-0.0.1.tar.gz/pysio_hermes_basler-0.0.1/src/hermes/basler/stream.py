############
#
# Copyright (c) 2024 Maxim Yudayev and KU Leuven eMedia Lab
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Created 2024-2025 for the KU Leuven AidWear, AidFOG, and RevalExo projects
# by Maxim Yudayev [https://yudayev.com].
#
# ############

from collections import OrderedDict

from hermes.base.stream import Stream


class CameraStream(Stream):
  """A structure to store Camera stream's data.
  """
  def __init__(self, 
               camera_mapping: dict[str, str],
               fps: float,
               resolution: tuple[int],
               timesteps_before_solidified: int = 0,
               update_interval_ms: int = 100,
               **_) -> None:
    super().__init__()

    camera_names, camera_ids = tuple(zip(*(camera_mapping.items())))
    self._camera_mapping: OrderedDict[str, str] = OrderedDict(zip(camera_ids, camera_names))
    self._update_interval_ms = update_interval_ms
    self._timesteps_before_solidified = timesteps_before_solidified

    self._define_data_notes()

    # Add a streams for each asynchronous camera.
    for camera_id, camera_name in self._camera_mapping.items():
      self.add_stream(device_name=camera_id,
                      stream_name='frame',
                      is_video=True,
                      color_format='bayer_rg8',
                      data_type='uint8',
                      sample_size=resolution,
                      sampling_rate_hz=fps,
                      is_measure_rate_hz=True,
                      data_notes=self._data_notes[camera_id]["frame"],
                      timesteps_before_solidified=self._timesteps_before_solidified)
      self.add_stream(device_name=camera_id,
                      stream_name='frame_timestamp',
                      data_type='float64',
                      sample_size=[1],
                      sampling_rate_hz=fps,
                      data_notes=self._data_notes[camera_id]["frame_timestamp"])
      self.add_stream(device_name=camera_id,
                      stream_name='frame_index',
                      data_type='float64',
                      sample_size=[1],
                      sampling_rate_hz=fps,
                      data_notes=self._data_notes[camera_id]["frame_index"])
      self.add_stream(device_name=camera_id,
                      stream_name='frame_sequence_id',
                      data_type='float64',
                      sample_size=[1],
                      sampling_rate_hz=fps,
                      data_notes=self._data_notes[camera_id]["frame_sequence_id"])
      self.add_stream(device_name=camera_id,
                      stream_name='toa_s',
                      data_type='float64',
                      sample_size=[1],
                      sampling_rate_hz=fps,
                      data_notes=self._data_notes[camera_id]['toa_s'])


  def get_fps(self) -> dict[str, float | None]:
    return {camera_name: super()._get_fps(camera_name, 'frame') for camera_name in self._camera_mapping.values()}


  def _define_data_notes(self):
    self._data_notes = {}
    
    for camera_id, camera_name in self._camera_mapping.items():
      self._data_notes.setdefault(camera_id, {})
      self._data_notes[camera_id]["frame"] = OrderedDict([
        ('Serial Number', camera_id),
        (Stream.metadata_data_headings_key, camera_name),
      ])
      self._data_notes[camera_id]["frame_timestamp"] = OrderedDict([
        ('Notes', 'Time of sampling of the frame w.r.t the camera onboard PTP clock.'),
      ])
      self._data_notes[camera_id]["frame_index"] = OrderedDict([
        ('Notes', 'Monotonically increasing index of the frame to track lost frames, '
                  'starting from 0 when the recording started.'),
      ])
      self._data_notes[camera_id]["frame_sequence_id"] = OrderedDict([
        ('Notes', 'Monotonically increasing index of the frame to track lost frames.'),
      ])
      self._data_notes[camera_id]['toa_s'] = OrderedDict([
        ('Notes', 'Time of arrival of the packet w.r.t. system clock.'),
      ])
