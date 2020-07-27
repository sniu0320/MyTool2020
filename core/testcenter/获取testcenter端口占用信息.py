# -*- coding: UTF-8 -*-

import sys
import os
import time
current_dir = os.path.split(os.path.realpath(__file__))[0]
if current_dir not in sys.path:
    sys.path.append(current_dir)
print(current_dir)

import StcPython as zte
######################################

stc = zte.StcPython()
print("Spirent TestCenter version : %s" % stc.get("system1", "version"))

######################################


def main():
    szChassisIpList = zte.readtxt('ChassisIpList.py')
    for szChassisIp in szChassisIpList:
        try:
            print('Connect to TestCenter Chassis : '+szChassisIp)
            stc.connect(szChassisIp)
        # except:
        except Exception:
            continue

    hChassisList = getChassis()
    pgLocationList = []
    BoardInfoDict = {}
    timestamp = time.strftime('%Y.%m.%d.%H.%M.%S')

    for hChassis in hChassisList:
        chassisProps = stc.get(hChassis)
        chassisIpAddr = chassisProps['Hostname']
        hTmList = getTestModules(hChassis)
        for hTm in hTmList:
            tmProps = stc.get(hTm)
            tmType = tmProps['PartNum']
            tmSlotIndex = tmProps['Index']
            hPgList = getPortGroups(hTm)
            for hPg in hPgList:
                pgProps = stc.get(hPg)
                pgSlotIndex = pgProps['Index']
                pgLocation = '//%s/%s/%s' % (chassisIpAddr,
                                             tmSlotIndex, pgSlotIndex)
                pgLocationList.append(pgLocation)
                if pgProps['OwnershipState'] != 'OWNERSHIP_STATE_RESERVED':
                    OwnerUser = '空闲'
                else:
                    OwnerUser = pgProps['OwnerUserId'] + \
                        '@' + pgProps['OwnerHostname']
                szTemp = '{:<25}{:<21}{:<21}'.format(
                    pgLocation, tmType, OwnerUser)
                BoardInfoDict[pgLocation] = szTemp

    print('Collect TestCenter TestModules Info ...')
    # 编写文件抬头
    item1 = r'测试仪端口'
    item2 = r'单板类型'
    item3 = r'使用人'
    item = '{:<30}{:<25}{:<22}'.format(item1, item2, item3)
    parting_line = '================================================================================'

    filename = 'TestCenter_UsageRate_info_' + timestamp + '.txt'
    with open(filename, 'wb') as f:
        f.write(item+'\r\n')
        f.write(parting_line+'\r\n')
        for pgLocation in pgLocationList:
            f.write(BoardInfoDict[pgLocation]+'\r\n')

    stc.perform("ChassisDisconnectAll")
    print('Collect TestCenter TestModules Info Finished! ...')


def getChassisManager():
    return stc.get('system1', 'children-PhysicalChassisManager')


def getChassis():
    hMgr = getChassisManager()
    Chassis = stc.get(hMgr, 'children-PhysicalChassis')
    return Chassis.split()


def getTestModules(hChassis):
    TestModules = stc.get(hChassis, 'children-PhysicalTestmodule')
    return TestModules.split()


def getPortGroups(hTm):
    PortGroups = stc.get(hTm, 'children-PhysicalPortgroup')
    return PortGroups.split()


def getPorts(hPg):
    Ports = stc.get(hPg, 'children-PhysicalPort')
    return Ports.split()


def getEthernetFiber(hPort):
    return stc.get(hPort, 'EthernetFiber')


def displayChassisInfo(hChassis):
    chassisProps = stc.get(hChassis)
    print(chassisProps['SerialNum'])


def displayEthernetFiberInfo(hEthernetFiber):
    fiberProps = stc.get(hEthernetFiber)
    print(fiberProps['ModuleType'])
    print(fiberProps['VendorName'])
    print(fiberProps['VendorSerialNumber'])


# ========================================================
main()
