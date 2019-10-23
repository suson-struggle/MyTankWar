"""
    新增功能：
        完善音效类
        1.开场音乐
        2.爆炸音效
"""

# 导入模块
import pygame, random, time, os
from pygame.sprite import Sprite

SCREEN_WIDTH = 800  # 窗口的宽度
SCRENN_HEIGHT = 700 # 窗口的高度
BGCOLOR = pygame.Color(0, 0, 0) # 窗口的背景颜色
TEXT_COLOR = pygame.Color(0, 255, 255)    # 文字的字体颜色
os.environ["SDL_VEDIO_WINDOW_POS"] = "{0}, {1}".format(300, 300)    # 窗口的固定位置

# 定义一个基类，继承精灵类
class BaseItem(Sprite):
    def __init__(self, color, width, height):
        pygame.sprite.Sprite.__init__(self)


# 主类
class MainGame():
    window = None   # 窗口对象
    my_tank = None  # 我方坦克对象
    enemyTankList = []  # 敌方坦克对象列表
    enemyTankCount = 10  # 敌方坦克对象数量
    myBulletList = []   # 我方子弹对象列表
    enemyBulletList = []    # 敌方子弹对象列表
    explodeList = []    # 爆炸效果对象列表
    wallList = []       # 墙壁对象列表
    death_time = 0      # 我方坦克死亡次数
    def __init__(self):
        pass
    # 开始游戏方法
    def startGame(self):
        pygame.display.init()   # 初始化pygame
        Music("start").play()
        MainGame.window = pygame.display.set_mode([SCREEN_WIDTH, SCRENN_HEIGHT])    # 创建窗口
        os.environ["SDL_VEDIO_WINDOW_POS"] = "{0}, {1}".format(100, 100)    # 设置固定窗口位置
        pygame.display.set_caption("坦克大战1.0")   # 修改窗口标题
        # 创建我方坦克对象
        MainGame.my_tank = Tank(350, 250)   # 调用这个对象，则返回的也是一个对象，具有初始化中的属性
        # 创建坦克对象, 并添加到敌方坦d克列表
        self.createEnemyTank()
        # 创建墙壁对象
        self.createWall()
        # 使用一个死循环让程序一直运行，循环显示窗口
        while True:
            time.sleep(0.008)
            MainGame.window.fill(BGCOLOR)  # 填充窗口背景色
            self.getEvent() # 获取事件（退出和键盘按下）
            # 在窗口（20,20）位置显示文字 --》 将创建好的文字surface（表面）贴到主窗口
            MainGame.window.blit(self.getTextSurface("剩余敌方坦克数量：{0}".format(len(MainGame.enemyTankList)), 18), (20, 20))
            MainGame.window.blit(self.getTextSurface("死亡次数：{0}".format(MainGame.death_time), 18), (20, 40))
            if MainGame.my_tank and MainGame.my_tank.live:
                MainGame.my_tank.display()  # 显示我方坦克
            else:
                MainGame.my_tank = None
            self.blitEnemyTank()    # 显示敌方坦克
            self.blitMyBullet()     # 显示我方子弹
            self.blitEnemyBullet()  # 显示敌方子弹
            self.blitExplode()      # 显示爆炸效果
            self.blitWall()     # 显示墙壁
            # 只有移动开关为不关闭时，才能让坦克移动
            if MainGame.my_tank and MainGame.my_tank.live:
                if not MainGame.my_tank.stop:
                    MainGame.my_tank.move()  # 让我方坦克一直移动，直到按键松开
                    MainGame.my_tank.hitWall()  # 移动后，检测是否有和墙壁碰撞
                    MainGame.my_tank.myTank_hit_enemyTank()     # 检测我方坦克是否与敌方坦克碰撞
            else:
                MainGame.window.blit(self.getTextSurface("按Esc键复活坦克！", 28), (300, 200))
            self.updateEnemyTank()
            self.updateWall()
            pygame.display.update() # 更新窗口

    # 判断墙壁是否全部消灭
    def updateWall(self):
        if len(MainGame.wallList) <= 0:
            MainGame.window.blit(self.getTextSurface("按r键刷新墙壁！", 30), (300, 20))
    # 判断坦克是否全部消灭
    def updateEnemyTank(self):
        if len(MainGame.enemyTankList) <= 0:
            MainGame.window.blit(self.getTextSurface("按e键刷新敌方坦克！", 28), (300, 300))
    # 显示墙壁
    def blitWall(self):
        for wall in MainGame.wallList:
            wall.display()
    # 创建墙壁对象，并添加到墙壁列表中
    def createWall(self):
        for i in range(6):
            # 创建对象
            wall = Wall(250, 130*i)
            # 添加到墙壁列表中
            MainGame.wallList.append(wall)
            # wall.display()

    # 显示爆炸效果
    def blitExplode(self):
        for explode in MainGame.explodeList:
            if explode.live:
                explode.display()
                if not pygame.mixer.music.get_busy():
                    Music("fire").play()
            else:
                MainGame.explodeList.remove(explode)
    # 显示敌方子弹
    def blitEnemyBullet(self):
        for enemyBullet in MainGame.enemyBulletList:
            # 判断敌方子弹是否存活
            if enemyBullet.live:
                enemyBullet.display()   # 显示敌方子弹
                enemyBullet.move()      # 敌方子弹移动
                enemyBullet.enemyBullet_hit_myTank()
                enemyBullet.hitBullet()
                enemyBullet.hitWall()
                enemyBullet.enemyBullet_hit_enemyTank()
            else:
                MainGame.enemyBulletList.remove(enemyBullet)
    # 显示我方子弹
    def blitMyBullet(self):
        for myBullet in MainGame.myBulletList:
            # 只有子弹是存活的才显示和移动子弹
            if myBullet.live:
                myBullet.display()  # 显示子弹
                myBullet.move()     # 移动子弹
                # 我方坦克移动之后调用坚持碰撞方法
                myBullet.myBullet_hit_enemyTank()
                myBullet.hitBullet()
                myBullet.hitWall()
            else:
                MainGame.myBulletList.remove(myBullet)
    # 创建敌方坦克对象，并添加到对象中
    def createEnemyTank(self):
        top = 100
        for i in range(MainGame.enemyTankCount):
            left = random.randint(0, 600)
            speed = random.randint(10, 20)
            enemyTank = EnemyTank(top, left, speed)
            MainGame.enemyTankList.append(enemyTank)

    # 显示敌方坦克
    def blitEnemyTank(self):
        for enemyTank in MainGame.enemyTankList:
            # 只有敌方坦克存活时才显示
            if enemyTank.live:
                enemyTank.display()
                enemyTank.randMove()  # 敌方坦克随机移动
                enemyTank.hitWall()     # 检测敌方坦克是否撞墙
                enemyTank.enemyTank_hit_myTank()    # 检测敌方坦克是否与我方坦克相撞
                # enemyTank.enemyTank_hit_enemyTank()
                enemyBullet = enemyTank.shot()  # shot方法采用随机数处理，所以有大部分情况返回None
                # 只有敌方子弹不为空时才将敌方子弹对象添加到敌方子弹对象列表
                if enemyBullet:
                    MainGame.enemyBulletList.append(enemyBullet)
            else:
                MainGame.enemyTankList.remove(enemyTank)
    # 游戏结束方法
    def endGame(self):
        print("游戏结束！")
        exit()
    # 获取文字surface（表面）需要传递文字内容和文字大小
    def getTextSurface(self, text, size):
        self.text = text    # 文字内容
        self.size = size    # 文字大小
        pygame.font.init()  # 初始化字体
        # 获取font字体对象
        font = pygame.font.SysFont("kaiti", 18) # ,SysFont表示从系统字体中获取字体
        textSurface = font.render(text, True, TEXT_COLOR)   # 将文字贴在一个surface上
        return textSurface  # 调用结束后将返回一这个surface

    # 获取事件方法
    def getEvent(self):
        eventList = pygame.event.get()  # 获取事件列表
        # 循环遍历事件列表
        for event in eventList:
            # 如果事件类型为退出，则调用游戏结束方法
            if event.type == pygame.QUIT:
                self.endGame()
            # 如果事件类型为键盘按下，则判断按下了哪个键，并做相应的操作
            if event.type == pygame.KEYDOWN:
                if MainGame.my_tank and MainGame.my_tank.live:
                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                        # print("按下了w键，坦克向上移动！")
                        MainGame.my_tank.direction = "U"
                        # MainGame.my_tank.move()
                        MainGame.my_tank.stop = False
                    elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        # print("按下了a键，坦克向左移动！")
                        MainGame.my_tank.direction = "L"
                        # MainGame.my_tank.move()
                        MainGame.my_tank.stop = False
                    elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                        # print("按下了s键，坦克向下移动！")
                        MainGame.my_tank.direction = "D"
                        # MainGame.my_tank.move()
                        MainGame.my_tank.stop = False
                    elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        # print("按下了d键，坦克向右移动！")
                        MainGame.my_tank.direction = "R"
                        # MainGame.my_tank.move()
                        MainGame.my_tank.stop = False
                    if event.key == pygame.K_SPACE or event.key == pygame.K_q:
                        # print("发射子弹")
                        if len(MainGame.myBulletList) <= 2:
                            if not pygame.mixer.music.get_busy():
                                Music("hit").play()
                            myBullet = Bullet(MainGame.my_tank)  # 创建我方子弹
                            MainGame.myBulletList.append(myBullet)  # 将子弹添加到我方子弹列表
                # 按下e键创建敌方坦克
                if event.key == pygame.K_e:
                    self.createEnemyTank()
                if event.key == pygame.K_r:
                    self.createWall()
                # 我方坦克不存活的情况下检测是否有按下Esc键，有的话则让我方坦克复活
                elif event.key == pygame.K_ESCAPE:
                        # print("按下Esc键")
                        MainGame.my_tank = Tank(350, 250)


            # 如果松开是方向键，则让坦克停止
            if event.type == pygame.KEYUP:
                if MainGame.my_tank and MainGame.my_tank.live:
                    if event.key == pygame.K_w or event.key == pygame.K_a or event.key == pygame.K_s or event.key == pygame.K_d:
                        MainGame.my_tank.stop = True


class Tank(BaseItem):
    def __init__(self, top, left):
        self.images = {
            'U':pygame.image.load('img/p1tankU.gif'),
            'L':pygame.image.load('img/p1tankL.gif'),
            'D':pygame.image.load('img/p1tankD.gif'),
            'R':pygame.image.load('img/p1tankR.gif'),
        }
        # 方向
        self.direction = "U"
        self.image = self.images[self.direction]
        self.rect = self.image.get_rect()
        self.rect.top = top
        self.rect.left = left
        self.speed = 5      # 坦克的速度
        self.stop = True    # 坦克的移动情况
        self.live = True    # 坦克的存活情况
        # 坦克移动前的坐标
        self.oldLeft = 0
        self.oldTop = 0

    def display(self):
        # 获取展示的对象
        self.image = self.images[self.direction]
        MainGame.window.blit(self.image, self.rect)
    def move(self):
        # 保留每次移动前的坐标
        self.oldLeft = self.rect.left
        self.oldTop = self.rect.top
        if self.direction == "U":
            if self.rect.top - self.speed >= 0:
                self.rect.top -= self.speed
            else:
                self.rect.top = 0
        elif self.direction == "D":
            if self.rect.top + self.speed < SCRENN_HEIGHT - self.rect.height:
                self.rect.top += self.speed
            else:
                self.rect.top = SCRENN_HEIGHT - self.rect.height
        elif self.direction == "L":
            if self.rect.left - self.speed > 0:
                self.rect.left -= self.speed
            else:
                self.rect.left = 0
        elif self.direction == "R":
            if self.rect.left + self.speed < SCREEN_WIDTH - self.rect.height:
                self.rect.left += self.speed
            else:
                self.rect.left = SCREEN_WIDTH - self.rect.height

    # 坦克射击，返回一个子弹对象
    def shot(self):
        return Bullet(self)

    # 回到上一次的移动前的坐标
    def stay(self):
        self.rect.left = self.oldLeft
        self.rect.top = self.oldTop

    # 判断坦克是否有撞墙
    def hitWall(self):
        for wall in MainGame.wallList:
            # 如果撞墙，回到上一次移动前的坐标
            if pygame.sprite.collide_rect(self, wall):
                # self.stop = True
                self.stay()

    def myTank_hit_enemyTank(self):
        for enemyTank in MainGame.enemyTankList:
            if pygame.sprite.collide_rect(self, enemyTank):
                self.stay()

    def enemyTank_hit_myTank(self):
        for enemyTank in MainGame.enemyTankList:
            if MainGame.my_tank and MainGame.my_tank.live:
                if pygame.sprite.collide_rect(enemyTank, MainGame.my_tank):
                    enemyTank.stay()

    # 敌方坦克与敌方坦克碰撞
    def enemyTank_hit_enemyTank(self):
        for i in range(len(MainGame.enemyTankList)):
            if len(MainGame.enemyTankList) > 0 and i < len(MainGame.enemyTankList) - 1:
                if pygame.sprite.collide_rect(MainGame.enemyTankList[i], MainGame.enemyTankList[i+1]):
                    MainGame.enemyTankList[i].stay()
                    MainGame.enemyTankList[i+1].stay()
class Mytank(Tank):
    def __init__(self):
        pass
        # self.live = True

class EnemyTank(Tank):
    def __init__(self, top, left, speed):
        super(EnemyTank, self).__init__(top, left)
        # 将四个方向的坦克图片加载进来以字典的方式
        self.images = {
            'U': pygame.image.load('img/enemy1U.gif'),
            'L': pygame.image.load('img/enemy1L.gif'),
            'D': pygame.image.load('img/enemy1D.gif'),
            'R': pygame.image.load('img/enemy1R.gif'),
        }
        # 坦克坦克方向为随机获得
        self.direction = self.randDirection()
        # 根据方向获取图片对象
        self.image = self.images[self.direction]
        # 获取区域
        self.rect = self.image.get_rect()
        # 将坦克的位置放入rect内
        self.rect.left = left
        self.rect.top = top
        self.speed = 1
        self.stop = False
        self.step = random.randint(40, 100)  # 坦克移动方向前需要的步数
        self.live = True

    # 随机生成敌方坦克移动方向
    def randDirection(self):
        directions = ["U", "D", "L", "R"]
        num = random.randint(0, 3)
        return directions[num]

    def randMove(self):
        if self.step <= 0:
            self.direction = self.randDirection()
            self.step = random.randint(40, 100)
        else:
            self.move()
            self.step -= 1

    # 重写shot方法，只有随机数小于10时才发射子弹，其余情况返回None
    def shot(self):
        num = random.randint(0, 100)
        if num < 10:
            return Bullet(self)


class Bullet(BaseItem):
    def __init__(self, tank):
        self.image = pygame.image.load("img\enemymissile.gif")
        self.direction = tank.direction
        self.rect = self.image.get_rect()
        #子弹的left和top与方向有关
        if self.direction == 'U':
            self.rect.left = tank.rect.left + tank.rect.width / 2 - self.rect.width / 2
            self.rect.top = tank.rect.top - self.rect.height
        elif self.direction == 'D':
            self.rect.left = tank.rect.left + tank.rect.width / 2 - self.rect.width / 2
            self.rect.top = tank.rect.top + tank.rect.height
        elif self.direction == 'L':
            self.rect.left = tank.rect.left - self.rect.width / 2 - self.rect.width / 2
            self.rect.top = tank.rect.top + tank.rect.width / 2 - self.rect.width / 2
        elif self.direction == 'R':
            self.rect.left = tank.rect.left + tank.rect.width
            self.rect.top = tank.rect.top + tank.rect.width / 2 - self.rect.width / 2
        self.speed = 6  # 子弹的速度
        self.live = True    # 子弹的存活状态

    def display(self):
        MainGame.window.blit(self.image, self.rect)
    def move(self):
        if self.direction == "U":
            if self.rect.top - self.speed > 0:
                self.rect.top -= self.speed
            else:
                self.rect.top = 0
                self.live = False
        elif self.direction == "D":
            if self.rect.top + self.speed < SCRENN_HEIGHT - self.rect.height:
                self.rect.top += self.speed
            else:
                self.rect.top = SCRENN_HEIGHT - self.rect.height
                self.live = False
        elif self.direction == "L":
            if self.rect.left - self.speed > 0:
                self.rect.left -= self.speed
            else:
                self.rect.left = 0
                self.live = False
        elif self.direction == "R":
            if self.rect.left + self.speed < SCREEN_WIDTH - self.rect.height:
                self.rect.left += self.speed
            else:
                self.rect.left = SCREEN_WIDTH - self.rect.height
                self.live = False

    # 我方子弹与敌方坦克碰撞
    def myBullet_hit_enemyTank(self):
        for enemyTank in MainGame.enemyTankList:
            if pygame.sprite.collide_rect(self, enemyTank):
                self.live = False
                enemyTank.live = False
                # 发生碰撞之后创建爆炸对象
                explode = Explode(enemyTank)
                MainGame.explodeList.append(explode)
                # Music("fire").play()

    # 敌方子弹与我方坦克碰撞
    def enemyBullet_hit_myTank(self):
        if MainGame.my_tank and MainGame.my_tank.live:
            if pygame.sprite.collide_rect(self, MainGame.my_tank):
                self.live = False
                MainGame.my_tank.live = False
                MainGame.death_time += 1
                # 创建爆炸效果对象
                explode = Explode(MainGame.my_tank)
                MainGame.explodeList.append(explode)
                # Music("fire").play()

    # 检测子弹是否与墙壁碰撞
    def hitWall(self):
        for wall in MainGame.wallList:
            # 如果碰撞，则让子弹消失，墙壁生命值减少
            if pygame.sprite.collide_rect(self, wall):
                self.live = False
                wall.hp -= 1
                # 如墙壁生命值小于等于0，则让墙壁消失，并从墙壁列表中删除
                if wall.hp <= 0:
                    wall.live = False
                    MainGame.wallList.remove(wall)

    # 检测我方子弹与敌方子弹碰撞
    def hitBullet(self):
        for myBullet in MainGame.myBulletList:
            for enemyBullet in MainGame.enemyBulletList:
                if pygame.sprite.collide_rect(myBullet, enemyBullet):
                    myBullet.live = False
                    enemyBullet.live = False

    # 检测敌方子弹与敌方坦克碰撞
    def enemyBullet_hit_enemyTank(self):
        for enemyTank in MainGame.enemyTankList:
            for enemyBullet in MainGame.enemyBulletList:
                if pygame.sprite.collide_rect(enemyBullet, enemyTank):
                    enemyBullet.live = False
                    # enemyTank.live = False  # 敌方坦克自相残杀


class Wall():
    def __init__(self, top, left):
        # 加载墙壁图片
        self.image = pygame.image.load("img/steels.gif")
        # 获取区域
        self.rect = self.image.get_rect()
        # 给left和top赋值
        self.rect.left = left
        self.rect.top = top
        self.hp = 5     # 墙壁的生命值
        self.live = True    # 墙壁的存活状态
        # self.count = 6      # 墙壁的数量

    # 显示墙壁
    def display(self):
        if self.live:
            MainGame.window.blit(self.image, self.rect)

class Explode():
    def __init__(self, tank):
        # 加载爆炸图片集
        self.images = [
            pygame.image.load("img/blast0.gif"),
            pygame.image.load("img/blast1.gif"),
            pygame.image.load("img/blast2.gif"),
            pygame.image.load("img/blast3.gif"),
            pygame.image.load("img/blast4.gif")
        ]
        self.rect = tank.rect   # 爆炸的位置由坦克决定
        self.step = 0   # 步数，索引
        self.image = self.images[self.step]     # 根据索引获取爆炸对象
        self.live = True    # 爆炸对象的存活状态

    # 由于这个方法会在循环内持续调用，所以这里只需要设置好一个爆炸对象即可
    # 循环内系统会多次判断碰撞，之后将五张图片都存放在爆炸效果列表内
    def display(self):
        # 根据索引获取爆炸对象
        if self.step < len(self.images):
            self.image = self.images[self.step]
            self.step += 1
        else:
            self.live = False
            self.step = 0
        # 展示爆炸效果
        MainGame.window.blit(self.image, self.rect)
class Music():
    def __init__(self, music):
        # 初始化混合器
        pygame.mixer.init()
        if music == "start":
            file = pygame.mixer.music.load("img/start.wav")
        elif music == "hit":
            file = pygame.mixer.music.load("img/hit.wav")
        elif music == "fire":
            file = pygame.mixer.music.load("img/fire.wav")
        # 加载音效文件
    def play(self):
        # if not pygame.mixer.music.get_busy():
        pygame.mixer.music.play()

if __name__ == "__main__":
    MainGame().startGame()