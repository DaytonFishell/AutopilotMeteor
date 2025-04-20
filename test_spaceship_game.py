import pytest
import pygame
import time
from unittest.mock import Mock, patch
from spaceship_game import main, Spaceship, Meteor, GameTracker

@pytest.fixture
def mock_pygame():
    with patch('spaceship_game.pygame') as mock:
        mock.init.return_value = None
        mock.display.set_mode.return_value = Mock()
        mock.time.Clock.return_value = Mock()
        mock.font.Font.return_value = Mock()
        mock.event.get.return_value = []
        yield mock

@pytest.fixture 
def mock_random():
    with patch('spaceship_game.random') as mock:
        mock.random.return_value = 0.1
        mock.choice.return_value = 'left'
        mock.randint.return_value = 1
        mock.uniform.return_value = 0
        yield mock

def test_main_game_loop(mock_pygame, mock_random):
    # Mock collision to end game after 2 frames
    original_hypot = pygame.math.hypot
    call_count = 0
    def mock_hypot(x, y):
        nonlocal call_count
        call_count += 1
        if call_count > 10:
            return 0  # Force collision
        return 100
    pygame.math.hypot = mock_hypot

    # Run main
    with patch('builtins.open', mock_open()):
        main()

    # Verify pygame was initialized and quit
    mock_pygame.init.assert_called_once()
    mock_pygame.quit.assert_called_once()

    # Verify screen was updated
    assert mock_pygame.display.flip.call_count > 0

    # Restore original hypot
    pygame.math.hypot = original_hypot

def test_game_over_collision(mock_pygame, mock_random):
    # Force immediate collision
    pygame.math.hypot = lambda x, y: 0
    
    with patch('builtins.open', mock_open()):
        main()

    # Verify game over screen was shown
    assert mock_pygame.display.flip.call_count >= 2
    mock_pygame.time.wait.assert_called_once_with(3000)

def test_quit_event(mock_pygame, mock_random):
    mock_pygame.event.get.return_value = [
        type('Event', (), {'type': pygame.QUIT})()
    ]
    
    with patch('builtins.open', mock_open()):
        main()

    mock_pygame.quit.assert_called_once()