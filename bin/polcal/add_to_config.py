import ahab
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("config", help="Pass in the config file.")
parser.add_argument("year", help="Year to add metadata from.")
args = parser.parse_args()

ahab.cfg.moby2ahabcfg(args.config, output="/tmp/ahab.cfg")
config = ahab.cfg.read_cfg("/tmp/ahab.cfg")

template_config = ahab.cfg.read_cfg("./codevpol_pointing_metadata.json")

# directories entry might still exist in old configs
try:
    config.pop('directories')
except KeyError:
    pass

if args.year in template_config.keys():
    try:
        config['offset_file'] = "./actpol_data_shared/RelativeOffsets/" + template_config[args.year]['ar%s'%(config['array'])]
        config['year'] = args.year
        #output_dir = template_config['codevpol_dir'] + "%s/ar%s/"%(args.year, config['array'])
        output_dir = template_config['codevpol_dir'] 
        ahab.ahab.check_dir(output_dir)
        ahab.cfg.write_cfg(output_dir + "cal_cfg_ar%s_%sghz_%s.json"%(config['array'], config['codev_inputs']['freq'], args.year), config)
    except KeyError:
        print "ar%s not present in %s"%(config['array'], args.year)
