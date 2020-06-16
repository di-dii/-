import sys
from time import sleep
import pygame
from bullet import Bullet
from alien import Alien

def check_keydown_events(event,ai_settings,screen,ship,bullets,stats,sb,aliens):
    if event.key == pygame.K_RIGHT:
        ship.moving_right = True
    if event.key == pygame.K_LEFT:
        ship.moving_left = True
    elif event.key==pygame.K_SPACE:
        fire_bullet(ai_settings,screen,ship,bullets)
    elif not stats.game_active and event.key == pygame.K_RETURN:
        restart_game(sb,stats, aliens, bullets, ai_settings, screen, ship)
    elif event.key==pygame.K_q:
        stats.store_high_score()
        sys.exit()

def check_keyup_events(event,ship):
    if event.key == pygame.K_RIGHT:
        ship.moving_right = False
    if event.key == pygame.K_LEFT:
        ship.moving_left = False



def restart_game(sb,stats,aliens,bullets,ai_settings,screen, ship):
    #重置游戏速度
    ai_settings.initialize_dynamic_settings()

    # 隐藏鼠标光标
    pygame.mouse.set_visible(False)

    # 重置游戏统计信息
    stats.reset_stats()
    stats.game_active = True

    # 清空外星人列表和子弹列表
    aliens.empty()
    bullets.empty()

    # 创建一群新的外星人，并让飞船居中
    create_fleet(ai_settings, screen, ship, aliens)
    ship.center_ship()

    #等级恢复初值1
    stats.level=1
    sb.prep_level()

    sb.prep_ships()


def check_play_button(ai_settings,screen,stats,sb,play_button,ship,aliens,bullets,mouse_x,mouse_y):
    '''在玩家单机play按钮时开始游戏'''
    bottom_clicked=play_button.rect.collidepoint(mouse_x,mouse_y)

    if bottom_clicked and not stats.game_active:
        restart_game(sb,stats, aliens, bullets, ai_settings, screen, ship)


def check_events(ai_settings,screen,stats,sb,play_button,ship,aliens,bullets):
    # 监听键盘和鼠标事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            stats.store_high_score()
            sys.exit()
        elif event.type==pygame.KEYDOWN:
            check_keydown_events(event,ai_settings,screen, ship,bullets,stats,sb,aliens)
        elif event.type==pygame.KEYUP:
            check_keyup_events(event, ship)
        elif event.type==pygame.MOUSEBUTTONDOWN:
            mouse_x,mouse_y=pygame.mouse.get_pos()
            check_play_button(ai_settings,screen,stats,sb,play_button,ship,aliens,bullets,mouse_x,mouse_y)


def fire_bullet(ai_settings,screen,ship,bullets):
    if len(bullets) < ai_settings.bullets_allowed:
        new_bullet = Bullet(ai_settings, screen, ship)
        bullets.add(new_bullet)



def get_number_aliens_x(ai_settings,alien_width):
    '''计算每行可容纳多少个外星人'''
    available_space_x=ai_settings.screen_width-2*alien_width
    number_aliens_x=int(available_space_x/(alien_width*2))
    return number_aliens_x

def create_alien(ai_settings,screen,aliens,alien_number,row_number):
    ''' #创造一个外星人并将其加入当前行'''
    alien = Alien(ai_settings, screen)
    alien_width = alien.rect.width
    alien.x = alien_width + 2 * alien_width * alien_number
    alien.rect.x = alien.x
    alien.rect.y=alien.rect.height+2*alien.rect.height*row_number
    aliens.add(alien)

def get_number_rows(ai_settings,ship_height,alien_height):
    '''计算屏幕可容纳多少行外星人'''
    available_space_y=ai_settings.screen_height-3*alien_height-ship_height
    number_rows=int(available_space_y/(2*alien_height))
    return  number_rows

def create_fleet(ai_settings,screen,ship,aliens):
    '''创建外星人群'''
    #外星人间距为外星人宽度
    alien=Alien(ai_settings,screen)
    number_aliens_x=get_number_aliens_x(ai_settings,alien.rect.width)
    number_rows=get_number_rows(ai_settings,ship.rect.height,alien.rect.height)

    #创建外星人
    for row_number in range(number_rows):
        for alien_number in range(number_aliens_x):
            create_alien(ai_settings, screen, aliens, alien_number,row_number)

def check_fleet_edges(ai_settings,aliens):
    '''有外星人到达边缘时采取相应的措施'''
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(ai_settings,aliens)
            break

def change_fleet_direction(ai_settings,aliens):
    '''将整群外星人下移，并改变它们的方向'''
    for alien in aliens.sprites():
        alien.rect.y+=ai_settings.fleet_drop_speed
    ai_settings.fleet_direction *= -1

def check_bullet_alien_collisions(ai_settings,screen,stats,sb,ship,aliens,bullets):
    '''相应子弹和外星人碰撞'''
    #检查子弹是否击中敌人，若有，则删除相应的子弹和外星人
    collisions=pygame.sprite.groupcollide(bullets,aliens,True,True)  #两个true表示将碰撞的两个物体都删除掉
    if collisions:
        for aliensx in collisions.values():
            stats.score += ai_settings.alien_points*len(aliensx)
            sb.prep_score()
        check_high_score(stats, sb)

    if len(aliens) == 0:
        #删除现有子弹，加快游戏节奏，并创建一群新的外星人
        bullets.empty()
        ai_settings.increase_speed()
        create_fleet(ai_settings,screen,ship,aliens)
        stats.level += 1
        sb.prep_level()

def ship_hit(ai_settings,stats,sb,screen,ship,aliens,bullets):
    '''响应被外星人撞到飞船'''
    if stats.ships_left>0:
        #将ships_left减1
        stats.ships_left-=1
        #更新记分牌
        sb.prep_ships()
        #清空外星人列表和子弹列表
        aliens.empty()
        bullets.empty()
        #创建一群新的外星人，并将飞船放到屏幕底端中央
        create_fleet(ai_settings,screen,ship,aliens)
        ship.center_ship()
        #暂停
        sleep(0.5)
    else:
        pygame.mouse.set_visible(True)
        stats.game_active=False

def check_aliens_bottom(ai_settings,stats,sb,screen,ship,aliens,bullets):
    '''检测是否有外星人到达了屏幕底端'''
    screen_rect=screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom>=screen_rect.bottom:
            #像飞船被撞到后一样处理
            ship_hit(ai_settings, stats, sb,screen, ship, aliens, bullets)
            break

def check_high_score(stats,sb):
    '''检查是否诞生了最高分'''
    if stats.score>stats.high_score:
        stats.high_score=stats.score
        sb.prep_high_score()

def update_aliens(ai_settings,stats,sb,screen,ship,aliens,bullets):
    '''更新外星人群的所有外星人的位置'''
    check_fleet_edges(ai_settings,aliens)
    aliens.update()

    #检测外星人和飞船之间的碰撞
    if pygame.sprite.spritecollideany(ship,aliens):
        ship_hit(ai_settings,stats,sb,screen,ship,aliens,bullets)

    #检测是否有外星人到达了屏幕底端
    check_aliens_bottom(ai_settings,stats,sb,screen,ship,aliens,bullets)

def update_bullets(ai_settings,screen,stats,sb,ship,aliens,bullets):
    '''更新子弹位置及清除消失的子弹'''
    bullets.update()
    #删除已消失的子弹
    for bullet in bullets.copy():
        if bullet.rect.bottom<=0:
            bullets.remove(bullet)

    check_bullet_alien_collisions(ai_settings, screen, stats, sb,ship, aliens, bullets)


def update_screen(ai_settings,screen,stats,sb,ship,aliens,bullets,play_button):
    '''更新屏幕上的图像，并切换到新屏幕'''
    # 每次循环都重绘屏幕
    screen.fill(ai_settings.bg_color)

    #重绘所有子弹
    for bullet in bullets.sprites():
        bullet.draw_bullet()
    ship.blitme()
    aliens.draw(screen)

    #显示得分
    sb.show_score()

    #如果游戏处于非活动状态，就绘制play按钮
    if not stats.game_active:
        play_button.draw_button()

    # 刷新最近绘制的屏幕
    pygame.display.flip()