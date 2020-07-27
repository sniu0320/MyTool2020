# -*- coding: UTF-8 -*-

import sys
import os
import time
# This loads the TestCenter library.
import StcPython as zte
stc = zte.StcPython()

current_dir = os.path.split(os.path.realpath(__file__))[0]
if current_dir not in sys.path:
    sys.path.append(current_dir)

# # This loads the TestCenter library.
# import StcPython as zte
# stc = zte.StcPython()


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
    hProject = stc.create("project")
    portLocationList = []
    hTestPortFiberInterfaceDict = {}
    timestamp = time.strftime('%Y.%m.%d.%H.%M.%S')

    for hChassis in hChassisList:
        chassisProps = stc.get(hChassis)
        chassisIpAddr = chassisProps['Hostname']
        hTmList = getTestModules(hChassis)
        for hTm in hTmList:
            tmProps = stc.get(hTm)
            if '100G' not in tmProps['Description']:
                continue
            tmSlotIndex = tmProps['Index']
            hPgList = getPortGroups(hTm)
            for hPg in hPgList:
                hPortList = getPorts(hPg)
                for hPort in hPortList:
                    portProps = stc.get(hPort)
                    portIndex = portProps['Index']
                    portLocation = '//%s/%s/%s' % (chassisIpAddr, tmSlotIndex, portIndex)
                    portLocationList.append(portLocation)
                    hTestPort = stc.create("port", under=hProject, location=portLocation, useDefaultHost=False)
                    hTestPortFiberInterfaceDict[portLocation] = stc.create("Ethernet100GigFiber",  under=hTestPort)

    print('ForceReservePorts...wait a moment...')
    stc.perform('ReservePort', Location=portLocationList, RevokeOwner=True)
    print('Attaching ports ...')
    stc.perform('AttachPorts')
    print('Apply configuration')
    stc.apply()

    print('Collect TestCenter OpticalModule SN Info ...')
    # 编写文件抬头
    item1 = r'测试仪端口'
    item2 = r'SN编号'
    item3 = r'类型'
    item4 = r'厂商'
    item = '{:<31}{:<22}{:<16}{:<22}'.format(item1, item2, item3, item4)
    parting_line = '================================================================================'

    filename_100g = 'TestCenter_opticalmodule_sn_info_100g_' + timestamp + '.txt'
    with open(filename_100g, 'wb') as f:
        f.write(item+'\r\n')
        f.write(parting_line+'\r\n')
        for portLocation in portLocationList:
            fiberProps = stc.get(hTestPortFiberInterfaceDict[portLocation])
            # print(fiberProps['ModuleType'])
            if fiberProps['ModuleType'] == 'ABSENT':
                continue
            # 光模块类型应该读取的是fiberProps['ModuleType'] ，而不是fiberProps['PersonalityCardType'] ，此处TestCenter有bug，把CFP2返回的值是CFP。这里是临时用法。

            szTemp = '{:<25}{:<21}{:<14}{:<22}'.format(portLocation, fiberProps['VendorSerialNumber'], fiberProps['PersonalityCardType'], fiberProps['VendorName'])
            f.write(szTemp+'\r\n')

    # Disconnect from chassis, release ports, and reset configuration.
    print('Release ports and disconnect from Chassis')
    stc.perform("ChassisDisconnectAll")
    stc.perform("ResetConfig")
    stc.delete(hProject)
    print('Collect TestCenter OpticalModule SN Info Finished! ...')


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
# ================================================================


main()
