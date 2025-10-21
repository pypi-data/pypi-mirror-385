import gaiaengine as gaia


class AoEAnim:
    IDLE, WALK, ATTACK, DECAY, DIE, RUN = range(6)


class AoEUnit(gaia.Unit):
    def __init__(self, *args):
        super().__init__(*args)

        self.walk_speed = 0.7
        self.run_speed = 1.4
        self.is_running = False
        self.is_dead = False

        self.walk_anim = AoEAnim.WALK if self.isAnimationLoaded(AoEAnim.WALK) else AoEAnim.IDLE

        self.onTargetOrDirectionSet.bind(self.start_moving_animation)
        self.onStoppedMoving.bind(self.start_idle_animation)

        self.startAnimation(AoEAnim.IDLE)

    def start_moving_animation(self):
        # If you weren't moving, start playing an animation
        if not self.is_dead and self.speed == 0.0:
            if self.is_running:
                self.run()
            else:
                self.walk()

    def walk(self):
        if not self.is_dead:
            self.speed = self.walk_speed
            self.is_running = False
            self.startAnimation(self.walk_anim)

    def run(self):
        if not self.is_dead:
            self.speed = self.run_speed
            self.is_running = True
            if self.isAnimationLoaded(AoEAnim.RUN):
                self.startAnimation(AoEAnim.RUN)
            else:
                self.startAnimation(self.walk_anim, self.run_speed / self.walk_speed)

    def start_idle_animation(self):
        if not self.is_dead:
            self.is_running = False
            if self.currentTexture != AoEAnim.IDLE:
                self.startAnimation(AoEAnim.IDLE)

    def decay(self):
        if self.isAnimationLoaded(AoEAnim.DECAY):
            self.startAnimation(AoEAnim.DECAY, self.delete)
        else:
            self.delete()

    def die(self):
        if not self.is_dead:
            self.setTarget(None)
            self.speed = 0.0
            self.is_dead = True
            self.type = -1
            self.canBeSelected = False

            if self.isAnimationLoaded(AoEAnim.DIE):
                self.startAnimation(AoEAnim.DIE, self.decay)
            else:
                self.decay()