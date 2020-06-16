import pygame

class Giao():
    '''遊戲音效，giao'''
    def __init__(self):
        pygame.mixer.init()
        self.giao_wav=pygame.mixer.Sound('music\giaoo.wav')
        pygame.mixer_music.load('music\\although we have nothing.mp3')
        pygame.mixer_music.play(-1,0)

