# -*- coding: UTF-8 -*-

import StcPython as zte
import sys
import os
import time
current_dir = os.path.split(os.path.realpath(__file__))[0]
if current_dir not in sys.path:
    sys.path.append(current_dir)

######################################

stc = zte.StcPython()
print("Spirent TestCenter version : %s" % stc.get("system1", "version"))

######################################


def main():
    # 初始化
    szChassisIpList = zte.readtxt('ChassisIpList.py')
    chassisLocationList = []
    chassisInfoDict = {}
    tmLocationList = []
    tmInfoDict = {}
    timestamp = time.strftime('%Y.%m.%d.%H.%M.%S')

    for szChassisIp in szChassisIpList:
        try:
            print('Connect to TestCenter Chassis : '+szChassisIp)
            stc.connect(szChassisIp)
        # except:
        except Exception:
            continue
    # 获取 Chassis 信息
    hChassisList = getChassis()
    for hChassis in hChassisList:
        chassisProps = stc.get(hChassis)
        chassisIpAddr = chassisProps['Hostname']
        chassisPartNum = chassisProps['PartNum']
        chassisSerialNum = chassisProps['SerialNum']
        chassisFirmwareVersion = chassisProps['FirmwareVersion']
        chassisLocation = '//%s' % chassisIpAddr
        chassisLocationList.append(chassisLocation)
        szTemp = '{:<24}{:<19}{:<15}{:<20}'.format(chassisLocation, chassisPartNum, chassisSerialNum,
                                                   chassisFirmwareVersion)
        chassisInfoDict[chassisLocation] = szTemp

        # 获取 TestModules 信息
        hTmList = getTestModules(hChassis)
        for hTm in hTmList:
            tmProps = stc.get(hTm)
            tmPartNum = tmProps['PartNum']
            tmSlotIndex = tmProps['Index']
            tmSerialNum = tmProps['SerialNum']
            tmFirmwareVersion = tmProps['FirmwareVersion']
            tmLocation = '//%s/%s' % (chassisIpAddr, tmSlotIndex)
            tmLocationList.append(tmLocation)
            szTemp = '{:<24}{:<19}{:<15}{:<20}'.format(
                tmLocation, tmPartNum, tmSerialNum, tmFirmwareVersion)
            tmInfoDict[tmLocation] = szTemp

    print('Collect TestCenter SerialNum Info ...')
    # 编写文件抬头
    item1 = r'Location'
    item2 = r'PartNum'
    item3 = r'SerialNum'
    item4 = r'FirmwareVersion'
    item = '{:<24}{:<19}{:<15}{:<20}'.format(item1, item2, item3, item4)
    parting_line = '============================================================================'

    filename = 'TestCenter_SerialNum_info_' + timestamp + '.txt'
    with open(filename, 'wb') as f:
        f.write(item+'\r\n')
        f.write(parting_line+'\r\n')
        for chassisLocation in chassisLocationList:
            f.write(chassisInfoDict[chassisLocation]+'\r\n')
        f.write(parting_line+'\r\n')
        for tmLocation in tmLocationList:
            f.write(tmInfoDict[tmLocation]+'\r\n')

    stc.perform("ChassisDisconnectAll")
    print('Collect TestCenter SerialNum Info Finished! ...')


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


main()
