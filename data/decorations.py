#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright Tim Henning 2014

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import NumericProperty, ObjectProperty
from kivy.uix.widget import Widget
import random


class MovingDecoration(Widget):
    """ Base class for widgets with three periodical moving elements """
    direction_0 = NumericProperty(1)
    direction_1 = NumericProperty(1)
    direction_2 = NumericProperty(1)
    segment_width_0 = NumericProperty(60)
    segment_width_1 = NumericProperty(40)
    segment_width_2 = NumericProperty(70)
    color_0 = ObjectProperty((1, 1, 1, 0.6))
    color_1 = ObjectProperty((1, 1, 1, 0.75))
    color_2 = ObjectProperty((1, 1, 1, 0.9))
    
    def __init__(self, **kwargs):
        super(MovingDecoration, self).__init__(**kwargs)
        self.segment_width_0 = 30 + random.random() * 100
        self.segment_width_1 = 30 + random.random() * 100
        self.segment_width_2 = 30 + random.random() * 100
        self.direction_0 = 1 if random.random() < 0.5 else -1
        self.direction_1 = 1 if random.random() < 0.5 else -1
        self.direction_2 = 1 if random.random() < 0.5 else -1
        self.speeds = [1.5 + random.random() * 4, 1.5 + random.random() * 4, 1.5 + random.random() * 4]

class RotatingDecoration(MovingDecoration):
    """ Base class for widgets with three rotating elements """
    angle_0 = NumericProperty(0)
    angle_1 = NumericProperty(0)
    angle_2 = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super(RotatingDecoration, self).__init__(**kwargs)
        self.offsets = (0, random.random() * 360, random.random() * 360)
        Clock.schedule_interval(self.start_animation_0, self.speeds[0])
        Clock.schedule_interval(self.start_animation_1, self.speeds[1])
        Clock.schedule_interval(self.start_animation_2, self.speeds[2])
        
    def start_animation_0(self, trigger=None, value=None):
        self.angle_0 = self.offsets[0]
        anim = Animation(angle_0=360+self.offsets[0], duration=self.speeds[0])
        anim.start(self)
    
    def start_animation_1(self, trigger=None, value=None):
        self.angle_1 = self.offsets[1]
        anim = Animation(angle_1=360+self.offsets[1], duration=self.speeds[1])
        anim.start(self)

    def start_animation_2(self, trigger=None, value=None):
        self.angle_2 = self.offsets[2]
        anim = Animation(angle_2=360+self.offsets[2], duration=self.speeds[2])
        anim.start(self)

class LinearDecoration(MovingDecoration):
    """ Base class for widgets with three linear moving elements """
    pos_0 = NumericProperty(0)
    pos_1 = NumericProperty(0)
    pos_2 = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super(LinearDecoration, self).__init__(**kwargs)
        self.offsets = (0, random.random(), random.random())
        Clock.schedule_interval(self.start_animation_0, self.speeds[0])
        Clock.schedule_interval(self.start_animation_1, self.speeds[1])
        Clock.schedule_interval(self.start_animation_2, self.speeds[2])
        
    def start_animation_0(self, trigger=None, value=None):
        self.pos_0 = self.offsets[0]
        anim = Animation(pos_0=1+self.offsets[0], duration=self.speeds[0])
        anim.start(self)
    
    def start_animation_1(self, trigger=None, value=None):
        self.pos_1 = self.offsets[1]
        anim = Animation(pos_1=1+self.offsets[1], duration=self.speeds[1])
        anim.start(self)

    def start_animation_2(self, trigger=None, value=None):
        self.pos_2 = self.offsets[2]
        anim = Animation(pos_2=1+self.offsets[2], duration=self.speeds[2])
        anim.start(self)

class PairValueDecoration(Widget):
    """ Base class for widgets with two linear moving lines.
    The "pair" is start and end of a line. """
    pos0_0 = NumericProperty(0)
    pos0_1 = NumericProperty(0)
    pos1_0 = NumericProperty(0)
    pos1_1 = NumericProperty(0)
    color_0 = ObjectProperty((1, 1, 1, 0.6))
    color_1 = ObjectProperty((1, 1, 1, 0.75))
    
    def __init__(self, **kwargs):
        super(PairValueDecoration, self).__init__(**kwargs)
        self.start_animation_0()
        self.start_animation_1()
        
    def start_animation_0(self, trigger=None, value=None):
        self.pos0_0 = 0
        self.pos0_1 = random.random() * -0.5
        speed_0 = 2 + random.random() * 2
        speed_1 = 2 + random.random() * 2
        anim = Animation(pos0_0=1, duration=speed_0)
        anim.start(self)
        anim = Animation(pos0_1=1, duration=speed_1)
        anim.start(self)
        Clock.schedule_once(self.start_animation_0, max(speed_0, speed_1))
    
    def start_animation_1(self, trigger=None, value=None):
        self.pos1_0 = 0
        self.pos1_1 = random.random() * -0.5
        speed_0 = 2 + random.random() * 2
        speed_1 = 2 + random.random() * 2
        anim = Animation(pos1_0=1, duration=speed_0)
        anim.start(self)
        anim = Animation(pos1_1=1, duration=speed_1)
        anim.start(self)
        Clock.schedule_once(self.start_animation_1, max(speed_0, speed_1))

class CircleDecoration(RotatingDecoration):
    pass

class GearDecoration(RotatingDecoration):
    pass

class CrossDecoration(RotatingDecoration):
    pass

class DotDecoration(RotatingDecoration):
    radius = NumericProperty(0)

class RingDecoration(RotatingDecoration):
    pass

class LineDecoration(PairValueDecoration):
    pass

class LinearDotsDecoration(LinearDecoration):
    pass

Builder.load_file("data/decorations.kv")