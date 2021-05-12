from numpy.random import normal
import random
import os
import subprocess
import json

with open('config.txt', 'r') as f:
    lilypath = f.read()

class Note:
    
    def __init__(self, start = 0, octave = 0):
        self.scale = ['c','d','e','f','g','a','b']
        self.current = start
        self.octave = octave
        
    def to_string(self):
        note = self.scale[self.current]
        octave_mark = ''
        if self.octave > 0:
            octave_mark = "'" * self.octave
        if self.octave < 0:
            octave_mark = "," * abs(self.octave)
        return str(self.scale[self.current]+octave_mark)
    
    def __add__(self, other):
        self.jump(other)
        
    def __sub__(self, other):
        self.jump(-1*other)
        
    def jump(self, steps):
        self.current += steps
        self.octave += self.current//7
        self.current %= 7
        
    def relative(self, relative_to):
        return self.current + relative_to * 7
        
class Instrument:
    def __init__(self, bot = -4, top = 32, name = 'violin'):
        self.variance = 2
        self.bottom_border = bot
        self.up_border = top
        self.start_octave = 1
        self.current = Note(octave = self.start_octave)
        self.jumps = []
        self.notes = []
        
    def gen_one(self):
        rests = ['r1', 'r2', 'r4', 'r8', 'r16', 'r32', 'r64', 'r128']
        if random.randint(0,10) == 0:
            self.notes.append(rests[random.randint(0,len(rests)-1)])
        down_offset = False
        up_offset = False
        random_offset = round(normal(scale=self.variance))
        
        while random_offset == 0: # take random offset until value is different from 0 - we don't want multiple notes one after another with the same pitch
            random_offset = round(normal(scale=self.variance))

        if self.current.relative(self.start_octave) + random_offset < self.bottom_border:
            print("{} is too low, jumping by {}".format(random_offset, random_offset+6))
            random_offset += 6
        if self.current.relative(self.start_octave) + random_offset > self.up_border:
            print("{} is too low, jumping by {}".format(random_offset, random_offset-6))
            random_offset -= 6
        
    
        self.current + random_offset
        
        self.jumps.append(random_offset)
        self.notes.append(self.current.to_string())
        if len(self.notes) >= 500:
            return False
        else:
            return True
    
    
    def gen_n(self, n):
        for i in range(n):
            if not self.gen_one():
                break
            
    def to_file(self, name = 'test.ly'):
        file = open(name,'w')
        file.write("{\n")
        file.write(' '.join(self.notes))
        file.write("\n}")
        file.close()



def render_note(output_dir, filename):
    try:
        subprocess.call([lilypath,'--png', '--output', output_dir + '/' + filename, './ly/' + filename +'.ly'])
    except Exception as e:
        print(e)
    os.remove('./ly/' + filename +'.ly')


def generate_notes(num = 5, output_dir = './output'):

    if not os.path.exists('./ly'):
        os.mkdir('./ly')
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    lables = {}
    for i in range(num):
        while True:
            instrument = Instrument()
            instrument.gen_n(50)
            if not(instrument.notes in list(lables.values())):
                break
        filename = 'note_' + str(i)
        instrument.to_file('./ly/' + filename +'.ly')
        render_note(output_dir, filename)
        lables[filename] = instrument.notes
    
    with open(output_dir + '/lables.json', 'w', encoding='utf-8') as f:
        json.dump(lables, f, ensure_ascii=False, indent=4)
        



if __name__ == "__main__":
    generate_notes()
