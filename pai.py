'''
 * Copyright@Lcenter
 * Author:TuYongXuan
 * Date:2019-09-20
 * Description:PaiServer
'''

import PaiCore
import PaiCommon as cfg

for configure in cfg.HttpServer:
    PaiCore.RunCore(cfg.Processes, configure)