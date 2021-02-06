import keyboard
import pymem
from threading import Thread, Condition, Lock
from math import sqrt, pi, isnan, atan
import time
from offsets import *

pm = pymem.Pymem("csgo.exe")
client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll
engine = pymem.process.module_from_name(pm.process_handle, "engine.dll").lpBaseOfDll
enginepointer = pm.read_int(engine + dwClientState)
"""print('Set Smooth Value(1-2000)')
smooth = int(input())
print('Set Fov Value(1-26)')
aimfov = int(input())
print('Set AimBone [8:HEAD, 7:NECK, 6:CHEST, 5:BODY])')
aimbone = int(input())"""


def checkindex():
    while True:
        localplayer = pm.read_int(client + dwLocalPlayer)
        for y in range(64):
            if pm.read_int(client + dwEntityList + y * 0x10):
                entity = pm.read_int(client + dwEntityList + y * 0x10)
                if localplayer == entity:
                    return y


def radar():
    if pm.read_int(client + dwLocalPlayer):
        localplayer = pm.read_int(client + dwLocalPlayer)
        localplayer_team = pm.read_int(localplayer + m_iTeamNum)
        for i in range(64):
            if pm.read_int(client + dwEntityList + i * 0x10):
                entity = pm.read_int(client + dwEntityList + i * 0x10)
                entity_team = pm.read_int(entity + m_iTeamNum)
                if entity_team != localplayer_team:
                    pm.write_int(entity + m_bSpotted, 1)


def buny():
    if pm.read_int(client + dwLocalPlayer):
        player = pm.read_int(client + dwLocalPlayer)
        force_jump = client + dwForceJump
        on_ground = pm.read_int(player + m_fFlags)

        if keyboard.is_pressed("space"):
            if on_ground == 257:
                pm.write_int(force_jump, 5)
                time.sleep(0.18)
                pm.write_int(force_jump, 4)


def no_flash():
    if pm.read_int(client + dwLocalPlayer):
        localplayer = pm.read_int(client + dwLocalPlayer)
        try:
            flash_value = localplayer + m_flFlashMaxAlpha
            pm.write_float(flash_value, float(0))
            time.sleep(0.0001)
        except pymem.exception.MemoryReadError:
            pass
        except pymem.exception.MemoryWriteError:
            pass


def rcs():
    oldpunchx = 0.0
    oldpunchy = 0.0
    if pm.read_int(client + dwLocalPlayer):
        time.sleep(0.01)
        rcslocalplayer = pm.read_int(client + dwLocalPlayer)
        rcsengine = pm.read_int(engine + dwClientState)
        if pm.read_int(rcslocalplayer + m_iShotsFired) > 2:
            rcs_x = pm.read_float(rcsengine + dwClientState_ViewAngles)
            rcs_y = pm.read_float(rcsengine + dwClientState_ViewAngles + 0x4)
            punchx = pm.read_float(rcslocalplayer + m_aimPunchAngle)
            punchy = pm.read_float(rcslocalplayer + m_aimPunchAngle + 0x4)
            newrcsx = rcs_x - (punchx - oldpunchx) * 2
            newrcsy = rcs_y - (punchy - oldpunchy) * 2
            oldpunchx = punchx
            oldpunchy = punchy
            if nanchecker(newrcsx, newrcsy) and checkangles(newrcsx, newrcsy):
                pm.write_float(rcsengine + dwClientState_ViewAngles, newrcsx)
                pm.write_float(rcsengine + dwClientState_ViewAngles + 0x4, newrcsy)
        else:
            oldpunchx = 0.0
            oldpunchy = 0.0


#rcs = Thread(target=rcs)
#rcs.start()


def get_player_info():
    ranks = ["No Rank", "Silver 1", "Silver 2", "Silver 3", "Silver 4", "Silver 5", "Silver 6", "Gold Nova 1",
             "Gold Nova 2", "Gold Nova 3", "Gold Nova 4", "Master Guardian 1", "Master Guardian 2", "Master Guardian 3",
             "DMG", "Legendary Eagle", "LEM", "Supreme", "Global Elite"]
    if pm.read_int(client + dwLocalPlayer):
        for x in range(64):
            cspr = pm.read_int(client + dwPlayerResource)
            try:
                ranknum = pm.read_int(cspr + m_iCompetitiveRanking + (x)*0x04)
                print(ranks[ranknum])
                """
                wins = pm.read_int(cspr + m_iCompetitiveWins + (x+1) * 0x04))

                radar_base = pm.read_int(client + dwRadarBase)
                c_hud_radar = pm.read_int(radar_base + 0x74)
                name = pm.read_string(c_hud_radar + 0x300 + 0x174 * (x))
                if name == "Joki4":
                    print("Name: " + name)
                    print("Rank: " + ranks[ranknum])
                    print("Wins: " + str(wins))
                    print()"""

            except pymem.exception.MemoryReadError:
                pass


# get_player_info()


def trigger():
    if pm.read_int(client + dwLocalPlayer):
        localplayer = pm.read_int(client + dwLocalPlayer)
        localplayer_team = pm.read_int(localplayer + m_iTeamNum)
        entity1 = pm.read_int(localplayer + m_iCrosshairId)
        if 64 >= entity1 > 0:
            entity2 = pm.read_int(client + dwEntityList + (entity1 - 1) * 0x10)
            entity_team = pm.read_int(entity2 + m_iTeamNum)
            gungameimmunity = pm.read_int(entity2 + m_bGunGameImmunity)
            if localplayer_team != entity_team and pm.read_int(client + dwForceAttack) != 5 and gungameimmunity != 1:
                for x in range(3):
                    shooting = True
                    pm.write_int(client + dwForceAttack, 5)
                    pm.write_int(client + dwForceAttack, 4)
                if localplayer_team != entity_team and shooting == True:
                    shooting = False
                    pm.write_int(client + dwForceAttack, 4)


#t = Thread(target=trigger)
#t.start()


def nanchecker(first, second):
    if isnan(first) or isnan(second):
        return False
    else:
        return True


def calc_distance(current_x, current_y, new_x, new_y):
    distancex = new_x - current_x
    if distancex < -89:
        distancex += 360
    elif distancex > 89:
        distancex -= 360
    if distancex < 0.0:
        distancex = -distancex

    distancey = new_y - current_y
    if distancey < -180:
        distancey += 360
    elif distancey > 180:
        distancey -= 360
    if distancey < 0.0:
        distancey = -distancey
    return distancex, distancey


def checkangles(x, y):
    if x > 89:
        return False
    elif x < -89:
        return False
    elif y > 360:
        return False
    elif y < -360:
        return False
    else:
        return True


def normalizeAngles(viewAngleX, viewAngleY):
    if viewAngleX > 89:
        viewAngleX -= 360
    if viewAngleX < -89:
        viewAngleX += 360
    if viewAngleY > 180:
        viewAngleY -= 360
    if viewAngleY < -180:
        viewAngleY += 360
    return viewAngleX, viewAngleY


def Distance(src_x, src_y, src_z, dst_x, dst_y, dst_z):
    diff_x = src_x - dst_x
    diff_y = src_y - dst_y
    diff_z = src_z - dst_z
    return sqrt(diff_x * diff_x + diff_y * diff_y + diff_z * diff_z)


def GetBestTarget(aimbone):
    while True:
        olddist = 111111111111
        newdist = 0
        target = None
        aimlocalplayer = pm.read_int(client + dwLocalPlayer)
        localplayer_team = pm.read_int(aimlocalplayer + m_iTeamNum)
        for x in range(64):
            if pm.read_int(client + dwEntityList + x * 0x10):
                entity = pm.read_int(client + dwEntityList + x * 0x10)
                entity_hp = pm.read_int(entity + m_iHealth)
                spotted = pm.read_int(entity + m_bSpottedByMask)
                index = checkindex()
                entity_team = pm.read_int(entity + m_iTeamNum)
                if spotted == 1 << index and localplayer_team != entity_team and entity_hp > 0:
                    entity_bones = pm.read_int(entity + m_dwBoneMatrix)
                    localpos_z = pm.read_float(aimlocalplayer + m_vecOrigin + 8)
                    localpos_x_angles = pm.read_float(enginepointer + dwClientState_ViewAngles)
                    localpos_y_angles = pm.read_float(enginepointer + dwClientState_ViewAngles + 0x4)
                    localpos_z_angles = pm.read_float(aimlocalplayer + m_vecViewOffset + 0x8) + localpos_z
                    entitypos_x = pm.read_float(entity_bones + 0x30 * aimbone + 0xC)
                    entitypos_y = pm.read_float(entity_bones + 0x30 * aimbone + 0x1C)
                    entitypos_z = pm.read_float(entity_bones + 0x30 * aimbone + 0x2C)

                    newdist = Distance(localpos_x_angles, localpos_y_angles, localpos_z_angles, entitypos_x,
                                       entitypos_y, entitypos_z)
                    if newdist < olddist:
                        olddist = newdist
                        target = entity
        if target and entity_hp > 0:
            return target


def aimthread(aimbone, aimfov, smooth):
    aimlocalplayer = pm.read_int(client + dwLocalPlayer)
    aimplayer = GetBestTarget(aimbone)
    aimplayer_hp = pm.read_int(aimplayer + m_iHealth)
    aimplayerbone = pm.read_int(aimplayer + m_dwBoneMatrix)
    localpos1 = pm.read_float(aimlocalplayer + m_vecOrigin)
    localpos2 = pm.read_float(aimlocalplayer + m_vecOrigin + 4)
    localpos_z_angles = pm.read_float(aimlocalplayer + m_vecViewOffset + 0x8)
    localpos3 = pm.read_float(aimlocalplayer + m_vecOrigin + 8) + localpos_z_angles
    enemypos1 = pm.read_float(aimplayerbone + 0x30 * aimbone + 0xC)
    enemypos2 = pm.read_float(aimplayerbone + 0x30 * aimbone + 0x1C)
    enemypos3 = pm.read_float(aimplayerbone + 0x30 * aimbone + 0x2C)
    viewanglex = pm.read_float(enginepointer + dwClientState_ViewAngles)
    viewangley = pm.read_float(enginepointer + dwClientState_ViewAngles + 0x4)
    delta_x = localpos1 - enemypos1
    delta_y = localpos2 - enemypos2
    delta_z = localpos3 - enemypos3
    hyp = sqrt(delta_x * delta_x + delta_y * delta_y + delta_z * delta_z)
    x = atan(delta_z / hyp) * 180 / pi
    y = atan(delta_y / delta_x) * 180 / pi
    if delta_x >= 0.0:
        y += 180.0
    diff_x = x - viewanglex
    diff_y = y - viewangley
    diff_x, diff_y = normalizeAngles(diff_x, diff_y)
    distancex = x - viewanglex
    if distancex < -89:
        distancex += 360
    elif distancex > 89:
        distancex -= 360
    if distancex < 0.0:
        distancex = -distancex

    distancey = y - viewangley
    if distancey < -180:
        distancey += 360
    elif distancey > 180:
        distancey -= 360
    if distancey < 0.0:
        distancey = -distancey

    if distancex < aimfov and distancey < aimfov and aimplayer_hp > 0:
        pm.write_float(enginepointer + dwClientState_ViewAngles, viewanglex + (diff_x / smooth))
        pm.write_float(enginepointer + dwClientState_ViewAngles + 0x4, viewangley + (diff_y / smooth))


def wallhack():
    if pm.read_int(client + dwLocalPlayer):
        for x in range(64):
            localplayer = pm.read_int(client + dwLocalPlayer)
            localplayer_team = pm.read_int(localplayer + m_iTeamNum)
            if pm.read_int(client + dwEntityList + x * 0x10):
                entity = pm.read_int(client + dwEntityList + x * 0x10)
                spotted = pm.read_int(entity + m_bSpottedByMask)
                index = checkindex()
                entity_team = pm.read_int(entity + m_iTeamNum)
                glow_manager = pm.read_int(client + dwGlowObjectManager)
                entity_glow = pm.read_int(m_iGlowIndex + entity)
                if entity and entity_team != localplayer_team and spotted == 1 << index:
                    pm.write_float(glow_manager + entity_glow * 0x38 + 0x4, float(3))  # R
                    pm.write_float(glow_manager + entity_glow * 0x38 + 0x8, float(0))  # G
                    pm.write_float(glow_manager + entity_glow * 0x38 + 0xC, float(2.5))  # B
                    pm.write_float(glow_manager + entity_glow * 0x38 + 0x10, float(1))
                    pm.write_int(glow_manager + entity_glow * 0x38 + 0x24, 1)
                elif spotted != 1 << index and entity and entity_team != localplayer_team:
                    pm.write_float(glow_manager + entity_glow * 0x38 + 0x8, float(1))  # G
                    pm.write_float(glow_manager + entity_glow * 0x38 + 0xC, float(0))  # B
                    pm.write_float(glow_manager + entity_glow * 0x38 + 0x10, float(1))
                    pm.write_int(glow_manager + entity_glow * 0x38 + 0x24, 1)


class ModelThread(Thread):
    process = None
    params = None

    def __init__(self):
        Thread.__init__(self)
        self.paused = False
        self.pause_cond = Condition(Lock())

    def run(self):
        while True:
            with self.pause_cond:
                while self.paused:
                    self.pause_cond.wait()
                if self.params:
                    self.process(*self.params)
                else:
                    self.process()

    def pause(self):
        self.paused = True
        self.pause_cond.acquire()

    def resume(self):
        self.paused = False
        self.pause_cond.notify()
        self.pause_cond.release()


Wallhack = ModelThread()
Wallhack.process = wallhack

Bunny = ModelThread()
Bunny.process = buny

Radar = ModelThread()
Radar.process = radar

#NoFlash = ModelThread()
#NoFlash.process = no_flash

RCS = ModelThread()
RCS.process = rcs

Trigger = ModelThread()
Trigger.process = trigger


AimBot = ModelThread()
AimBot.params = 8, 1, 1
AimBot.process = aimthread
