import sys
import pygame
from time import sleep

from bullet import Bullet
from alien import Alien


def check_events(ai_settings, screen, stats, play_button, ship, aliens,
        bullets):
    """Respoind to keypresses and mouse events."""

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event, ai_settings, screen, stats,
                play_button, ship, aliens, bullets)
        elif event.type == pygame.KEYUP:
            check_keyup_events(event, ship)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            check_play_button(ai_settings, screen, stats, play_button, ship,
                aliens, bullets, mouse_x, mouse_y)

def check_play_button(ai_settings, screen, stats, play_button, ship, aliens,
        bullets, mouse_x, mouse_y):
    """Start a new game when the player clicks Play."""
    button_clicked = play_button.rect.collidepoint(mouse_x, mouse_y)
    if button_clicked and not stats.game_active:
        # Reset the game settings.
        ai_settings.initialize_dynamic_settings()
        start_game(ai_settings, screen, stats, ship, aliens, bullets)
        
def start_game(ai_settings, screen, stats, ship, aliens, bullets):
    """Complete actions for starting a new game."""
    # Hide the mouse cursor.
    pygame.mouse.set_visible(False)

    # Reset the game statistics.
    stats.reset_stats
    stats.game_active = True

    # Empty the list of aliens and bullets.
    aliens.empty()
    bullets.empty()

    # Create a new fleet and center the ship.
    create_fleet(ai_settings, screen, ship, aliens)
    ship.center_ship()  

def check_keydown_events(event, ai_settings, screen, stats, play_button,
        ship, aliens, bullets):
    """Respond to keypresses."""

    if event.key == pygame.K_RIGHT:
        ship.moving_right = True
    elif event.key == pygame.K_LEFT:
        ship.moving_left = True
    elif event.key == pygame.K_SPACE:
        fire_bullet(ai_settings, screen, ship, bullets)
    elif event.key == pygame.K_p:
        start_game(ai_settings, screen, stats, ship, aliens, bullets)
    elif event.key == pygame.K_q:
        sys.exit()
    elif event.key == pygame.K_m:
        ai_settings.hesoyam += 1
        check_events(ai_settings, screen, stats, play_button, ship, aliens,
            bullets)
    elif event.key == pygame.K_a and ai_settings.hesoyam == 1:
        ai_settings.hesoyam = 2
        check_events(ai_settings, screen, stats, play_button, ship, aliens,
            bullets)
    elif event.key == pygame.K_i and ai_settings.hesoyam == 2:
        ai_settings.hesoyam = 3
        check_events(ai_settings, screen, stats, play_button, ship, aliens,
            bullets)
    elif event.key == pygame.K_n and ai_settings.hesoyam == 3:
        ai_settings.hesoyam = 4
        check_events(ai_settings, screen, stats, play_button, ship, aliens,
            bullets)
    elif event.key == pygame.K_a and ai_settings.hesoyam == 4:
        ai_settings.bullet_width = 300


def fire_bullet(ai_settings, screen, ship, bullets):
    """Fire a bullet if limit not reached."""

    # Create a new bullet and add it to the bullets group.
    if len(bullets) < ai_settings.bullets_allowed:
        new_bullet = Bullet(ai_settings, screen, ship)
        bullets.add(new_bullet)

def check_keyup_events(event, ship):
    """Respond to keyreleases."""

    if event.key == pygame.K_RIGHT:
        ship.moving_right = False
    elif event.key == pygame.K_LEFT:
        ship.moving_left = False

def update_screen(ai_settings, screen, stats, sb, ship, aliens, bullets,
        play_button):
    """Update the images on the screen and flip to the new screen."""

    # Redraw the screen during each pass through the loop.
    # First fill the background and then draw the ship over the background.
    screen.fill(ai_settings.bg_color)
    
    # Redraw all the bullets behind ship and aliens.
    for bullet in bullets.sprites():
        bullet.draw_bullet()

    ship.blitme()
    aliens.draw(screen)
    sb.show_score()

    # Draw the play button if the game is inactive.
    if not stats.game_active:
        play_button.draw_button()

    # Make the most recently drawn screen visible.
    pygame.display.flip()

def update_bullets(ai_settings, screen, stats, sb, ship, aliens, bullets):
    """Update position of bullets and get rid of old bullets."""
    # Update bullet positions.
    bullets.update()

    # Get rid of bullets that have disappeared.
    for bullet in bullets.copy():
        if bullet.rect.bottom <= 0:
            bullets.remove(bullet)

    # Check for any bullets that have hit aliens.
    check_bullet_alien_collisions(ai_settings, screen, stats, sb, ship, 
        aliens, bullets)

def check_bullet_alien_collisions(ai_settings, screen, stats, sb, ship, aliens,
        bullets):
    """Respond to bullet-alien collisions."""
    # Remove any bullets and aliens that have collided
    collisions = pygame.sprite.groupcollide(bullets, aliens, True, True)
    if collisions:
        for aliens in collisions.values():
            stats.score += ai_settings.alien_points * len(aliens)
            sb.prep_score()
    if len(aliens) == 0:
        # Destroy existing bullets, speed up the game and create new fleet.
        bullets.empty()
        ai_settings.increase_speed()
        create_fleet(ai_settings, screen, ship, aliens)

def ship_hit(ai_settings, stats, screen, ship, aliens, bullets):
    """Respong to ship being hit by alien."""
    if stats.ships_left > 0:
        # Decrement ships left.
        stats.ships_left -= 1

        # Empty the list of aliens and bullets.
        aliens.empty()
        bullets.empty()

        # Create a new fleet and center the ship.
        create_fleet(ai_settings, screen, ship, aliens)
        ship.center_ship()

        # Pause
        sleep(0.5)
    else:
        stats.game_active = False
        pygame.mouse.set_visible(True)

def check_aliens_bottom(ai_settings, stats, screen, ship, aliens, bullets):
    """Check if any aliens have hit the ship"""
    screen_rect = screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom >= screen_rect.bottom:
            # Treat this case as if an alien has hit the ship.
            ship_hit(ai_settings, stats, screen, ship, aliens, bullets)
            break

def update_aliens(ai_settings, stats, screen, ship, aliens, bullets):
    """Check if the fleet is at an edge and then update positions"""
    check_fleet_edges(ai_settings, aliens)
    aliens.update()

    # Look for alien-ship collisions.
    if pygame.sprite.spritecollideany(ship, aliens):
        ship_hit(ai_settings, stats, screen, ship, aliens, bullets)
    check_aliens_bottom(ai_settings, stats, screen, ship, aliens, bullets)

def create_alien(ai_settings, screen, aliens, alien_number, row_number):
    """Create an alien and place it in the row."""
    alien = Alien(ai_settings, screen)
    alien_width = alien.rect.width
    alien.x = alien_width + 2 * alien_width * alien_number
    alien.rect.x = alien.x
    alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
    aliens.add(alien)

def get_number_aliens_x(ai_settings, alien_width):
    """Determine the number of aliens that fit in a row."""
    available_space_x = ai_settings.screen_width - (2 * alien_width)
    number_aliens_x = int(available_space_x / (2 * alien_width))
    return number_aliens_x

def get_number_rows(ai_settings, ship_height, alien_height):
    """Determine the number of rows of aliens that fit on the screen."""
    available_space_y = (ai_settings.screen_height - 
                            (3 * alien_height) - ship_height)
    number_rows = int(available_space_y / (2 * alien_height))
    return number_rows

def create_fleet(ai_settings, screen, ship, aliens):
    """Create a fleet of aliens."""
    # Create an alien and find the number of aliens in a row.
    alien = Alien(ai_settings, screen)
    number_aliens_x = get_number_aliens_x(ai_settings, alien.rect.width)
    number_rows = get_number_rows(ai_settings, ship.rect.height,
        alien.rect.height)

    # Create the first row of aliens.
    for row_number in range(number_rows):
        for alien_number in range(number_aliens_x):
            # Create an alien and place it in the row.
            create_alien(ai_settings, screen, aliens, alien_number,
                row_number)

def check_fleet_edges(ai_settings, aliens):
    """Respond if any alien reaches either sides of the screen."""
    for alien in aliens:
        if alien.check_edges():
            change_fleet_direction(ai_settings, aliens)
            break

def change_fleet_direction(ai_settings, aliens):
    """Drop the entire fleet down and change the direction."""
    for alien in aliens.sprites():
        alien.rect.y += ai_settings.fleet_drop_speed
    ai_settings.fleet_direction *= -1

    
