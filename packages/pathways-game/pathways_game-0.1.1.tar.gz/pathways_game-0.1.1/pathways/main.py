import pygame
import os
import numpy as np


SQSIZE = 10


class Cards(object):
    def __init__(self):
        """
        Build cards, reset game state.
        """
        self.cards = self.make()
        self.reset()

    def __iter__(self):
        return self

    def __next__(self):
        """
        Return next card
        """
        self.card_num += 1
        if self.card_num >= self.cards.shape[0]:
            return None
        else:
            return self.cards[self.card_num]

    def make(self):
        """
        Generate array representing valid cards
        """
        c = [-1]*4
        return np.array(list('RYBG'))\
                   [np.array([[c[int(i)] for i in '0123112222113210']
                              for c[0] in range(4)
                              for c[1] in range(4)
                              for c[2] in range(4)
                              for c[3] in range(4)
                              if all([c[i+1] != c[i] for i in range(3)])
                                 and sum([(4**i)*j for i, j in enumerate(c)]) 
                                     > sum([(4**i)*j for i, j in enumerate(c[::-1])])
                                 and len(set(c)) < 4]).reshape(-1, 4, 4)]

    def reset(self):
        """
        Shuffle cards, rotate(flip) random half, reset card_num counter
        """
        sortix = np.argsort(np.random.random(self.cards.shape[0]))
        self.cards = self.cards[sortix]
        
        filt = np.random.random(self.cards.shape[0]) < 0.5
        self.cards[filt] = np.flip(self.cards[filt], axis=2)

        self.card_num = -1


class PlayArray(object):
    def __init__(self, dims, cards):
        """
        Capture dimensions and new card deck, reset play area
        """
        self.dims = dims
        self.cards = cards
        self.define_screen()
        self.reset()
        self.font = pygame.font.Font(os.path.join(os.path.dirname(__file__), 
                                                  'STENCIL.TTF'), 
                                     36)

    def define_screen(self):
        """
        Define screen display object, ensure dimensions are a multiple of SQSIZE
        """
        self.grid_dims = tuple(round(i/SQSIZE)+2 for i in self.dims[::-1])
        self.dims = tuple((i-2)*SQSIZE for i in self.grid_dims[::-1])
        self.screen = pygame.display.set_mode(self.dims)

    def center(self):
        """
        Return coordinates to plot card in center of play area
        """
        return tuple(int(i/2) for i in self.dims)
        
    def reset(self):
        """
        Reset playing area.
        """
        self.grid = np.full(self.grid_dims, '')
        self.cregion_map = -np.ones(self.grid_dims, dtype=int)
        self.cregion_sq = list()
        self.cregion_ct = -1
        self.score = 0
        self.screen.fill((0, 0, 0))

    def show_score(self, final=False):
        """
        Print score and number of cards remaining to screen
        """
        if final:
            sc_txt = f'Final score: {self.score}   '
            cl_txt = ' '*30
        else:
            sc_txt = f'Score: {self.score}   '
            cl_txt = f'   {42 - self.cards.card_num} cards left'
            
        sc_txt_img = self.font.render(sc_txt, 
                                      True, 
                                      (200, 200, 200),
                                      (0, 0, 0))
        sc_rect = sc_txt_img.get_rect()
        sc_rect.bottomleft = (20, self.dims[1]-20)
        self.screen.blit(sc_txt_img, sc_rect)

        cl_txt_img = self.font.render(cl_txt, 
                                      True, 
                                      (200, 200, 200),
                                      (0, 0, 0))
        cl_rect = cl_txt_img.get_rect()
        cl_rect.bottomright = (self.dims[0]-20, self.dims[1]-20)
        self.screen.blit(cl_txt_img, cl_rect)


def get_targ_region_indices():
    """
    Generate indices used on target region arrays for scoring.
    """
    raw_ix = np.array([[i-1.5, j-1.5] for i in range(4) for j in range(4)])
    raw_ix = raw_ix[np.ptp(np.abs(raw_ix), axis=1) == 0]
    
    edge_ix = (np.column_stack([raw_ix[:, j] if j == i else 2.5*np.sign(raw_ix[:, j]) 
                                for i in range(2) 
                                for j in range(2)]) + 2.5).astype(int)
    edge_ix = [i.reshape(-1, 2) for i in edge_ix]
    
    cardsq_ix = (np.array(raw_ix) + 2.5).astype(int)
    cardsq_ix2 = (np.column_stack([raw_ix[:, j] if j == i 
                                   else 1.5*np.sign(raw_ix[:, j]) 
                                   for i in range(2) 
                                   for j in range(2)]) + 2.5).astype(int)
    cardsq_ix = [np.concatenate((cardsq_ix[r:r+1],
                                 cardsq_ix2[r].reshape(-1, 2)
                                 [np.any(cardsq_ix2[r].reshape(-1, 2) != cardsq_ix[r:r+1], 
                                         axis=1)]))
                 for r in range(cardsq_ix.shape[0])]
    
    return cardsq_ix, edge_ix


class Card(pygame.sprite.Sprite):
    cellcolors = np.vectorize({'R': (255, 0, 0),
                               'Y': (255, 255, 0),
                               'G': (0, 255, 0),
                               'B': (0, 0, 255)}.get)
    targ_ix_cardsq, targ_ix_edges = get_targ_region_indices()
   
    def __init__(self, card, playarea, pos):
        super().__init__()
        self.card = card
        self.playarea = playarea

        # Set card image and position
        self.image = self.get_image()
        self.rect = self.image.get_rect()
        self.rect.center = pos

        # Create "memory" for sprite background
        self.bgstore = pygame.Surface(self.rect.size)

        # Place sprite on screen
        self.save_bg()
        self.blit()

    def get_image(self):
        """
        Create pygame image object for card
        """
        pixels = np.repeat(np.repeat(self.card, SQSIZE, axis=0), SQSIZE, axis=1)
        pixels = np.stack(self.cellcolors(pixels), axis=-1).astype(np.uint8)
        return pygame.image.frombytes(bytes(pixels.reshape(-1)), 
                                      tuple([SQSIZE*4]*2), 
                                      'RGB')

    def save_bg(self):
        """
        Save copy of background at self.rect
        """
        self.bgstore.blit(self.playarea.screen, (0, 0), self.rect)

    def blit(self):
        """
        Add card image at self.rect
        """
        self.playarea.screen.blit(self.image, self.rect)

    def restore_bg(self):
        """
        Restore saved background at self.rect
        """
        self.playarea.screen.blit(self.bgstore, self.rect)

    def move_to(self, pos):
        """
        Move card to new position.
        """
        self.restore_bg()
        self.rect.center = pos
        self.save_bg()
        self.blit()

    def rotate(self):
        """
        Rotate card
        """
        self.card = np.flip(self.card, axis=0)
        self.image = self.get_image()
        self.blit()

    def place(self, force=False):
        """
        Try to place card onto playing area, return True if successful
        """
        pos = self.rect.center
        grid_pos = tuple(round(i/SQSIZE)+1 for i in pos[::-1])
        
        # Fail if out of bounds
        if any([j for i in range(2)
                  for j in [grid_pos[i] < 3,
                            grid_pos[i] > self.playarea.grid.shape[i]-3]]):
            return False
        
        grid_ix = np.ix_(*[grid_pos[i] + np.arange(self.card.shape[i]+2) - 3
                           for i in range(2)])
        targ_colors = self.playarea.grid[grid_ix]
        
        # Fail if overlapping existing card
        if np.any(targ_colors[1:-1, 1:-1] != ''):
            return False

        # Fail if not adjacent to existing card (unless force is True)
        if (np.all(targ_colors[1:-1, [0, -1]] == '')
            and np.all(targ_colors[[0, -1], 1:-1] == '')
            and not force):
            return False

        # Add placed card to self.playarea.grid
        targ_colors[1:-1, 1:-1] = self.card
        self.playarea.grid[grid_ix] = targ_colors

        # Do scoring
        self.scoring(grid_ix)

        # Align card image to "grid" on screen
        scr_pos = tuple((i-1)*SQSIZE for i in grid_pos[::-1])
        self.move_to(scr_pos)

        return True

    def scoring(self, grid_ix):
        """
        Update region arrays, calculate score.
        """
        scoring_regions = set()
        for r in range(len(self.targ_ix_cardsq)):
            cardsq_ix = [[int(grid_ix[j][0, 0]+i[j])
                          for j in range(2)] 
                         for i in self.targ_ix_cardsq[r]]
            adj_regions = list({self.playarea.cregion_map[grid_ix][*self.targ_ix_edges[r][i]]
                                for i in range(2)
                                if self.playarea.grid[grid_ix][*self.targ_ix_edges[r][i]] 
                                    == self.playarea.grid[grid_ix][*self.targ_ix_cardsq[r][0]]})

            if len(adj_regions) == 0:
                self.playarea.cregion_ct += 1
                self.playarea.cregion_map[*zip(*cardsq_ix)] = self.playarea.cregion_ct
                self.playarea.cregion_sq += [cardsq_ix]
            else:
                if len(adj_regions) == 2:
                    r2ix = self.playarea.cregion_sq[adj_regions[1]]
                    self.playarea.cregion_sq[adj_regions[1]] = []
                    self.playarea.cregion_map[*zip(*r2ix)] = adj_regions[0]
                    self.playarea.cregion_sq[adj_regions[0]] += r2ix
                self.playarea.cregion_map[*zip(*cardsq_ix)] = adj_regions[0]
                self.playarea.cregion_sq[adj_regions[0]] += cardsq_ix
                scoring_regions.add(adj_regions[0])
        self.playarea.score += sum([len(self.playarea.cregion_sq[i]) 
                                    for i in scoring_regions])


def play():
    """
    Play the game!
    """
    # Initialize playing area
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pygame.init()

    # Initialize play area, card list; get first card (for icon image)
    pa = PlayArray((800, 600), Cards())
    card = Card(next(pa.cards), pa, pa.center())

    # Set window caption and icon
    pygame.display.set_caption("Pathways")
    pygame.display.set_icon(card.image)

    # Place first card at center of screen, get next card
    card.place(force=True)
    card = Card(next(pa.cards), pa, pa.center())
    pa.show_score()

    # Game loop
    run = True
    gameon = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE):
                run = False
            elif gameon:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if card.place():
                        nextcard = next(pa.cards)
                        if nextcard is None:
                            pa.show_score(final=True)
                            gameon = False
                        else:
                            card = Card(nextcard, pa, event.pos)
                            pa.show_score()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                    card.rotate()
                elif event.type == pygame.MOUSEMOTION:
                    card.move_to(event.pos)
                
        pygame.display.update()

    pygame.quit()