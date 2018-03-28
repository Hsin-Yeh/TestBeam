import FWCore.ParameterSet.Config as cms
import FWCore.ParameterSet.VarParsing as VarParsing

import os,sys

options = VarParsing.VarParsing('standard') # avoid the options: maxEvents, files, secondaryFiles, output, secondaryOutput because they are already defined in 'standard'
#Change the data folder appropriately to where you wish to access the files from:


options.register('inputFiles',
                '/afs/cern.ch/user/t/tquast/CMS_HGCal_Upgrade/studies/DNN-applications/checkpoints_model1/final',
                 VarParsing.VarParsing.multiplicity.list,
                 VarParsing.VarParsing.varType.string,
                 'Paths to the GAN model directory.'
                )

options.register('processedFile',
                 '/afs/cern.ch/user/t/tquast/Desktop/test.root',
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.string,
                 'Output file where pedestal histograms are stored')

options.register('electronicMap',
                 'map_CERN_Hexaboard_September_17Sensors_7EELayers_10FHLayers_V1.txt',
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.string,
                 'Name of the electronic map file in HGCal/CondObjects/data/')

options.register('beamEnergy',
                32,
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.int,
                 'Beam energy.'
                )

options.register('beamParticlePDGID',
                211,
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.int,
                 'Beam particles PDG ID.'
                )

options.register('setupConfiguration',
                2,
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.int,
                 'setupConfiguration.'
                )

options.register('layerPositionFile',
                 'layer_distances_CERN_Hexaboard_October_17Sensors_5EELayers_6FHLayers_V0.txt',
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.string,
                 'File indicating the layer positions in mm.')

options.register('GANModelIndex',
                "1",
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.string,
                 'Specify the used GAN model as "physics list" to be passed forward to the run data object.'
                )

options.register('NColorsInputImage',
                17,
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.int,
                 'Number of colours of input image for DNN analysis.'
                )

options.register('zDim',
                100,
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.int,
                 'Dimension of the random noise input vector.'
                )

options.register('areaSpecification',
                "H2",
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.string,
                 'Area which was used (for DWC simulation).'
                )

#Todo: insert into the plugin
options.register('noisyChannelsFile',
                 '/home/tquast/tb2017/pedestals/noisyChannels_1190.txt',
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.string,
                 'Channels which are noisy and excluded from the reconstruction')

#Todo: insert into the plugin
options.register('MaskNoisyChannels',
                1,
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.int,
                 'Ignore noisy channels in the reconstruction.'
                )

options.register('reportEvery',
                1000,
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.int,
                 'Path to the file from which the DWCs are read.'
                )

options.register('NEvents',
                1000,
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.int,
                 'Generate that many events.'
                )


options.parseArguments()

print options


electronicMap="HGCal/CondObjects/data/%s" % options.electronicMap

################################
process = cms.Process("rechitproducer")
process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(-1)
)
####################################
# Reduces the frequency of event count couts
process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = options.reportEvery
####################################



process.output = cms.OutputModule("PoolOutputModule",
                                  fileName = cms.untracked.string(options.processedFile),                                  
                                  outputCommands = cms.untracked.vstring('drop *',
                                                                         'keep *_*_HGCALTBRECHITS_*',
                                                                         'keep *_*_DelayWireChambers_*',
                                                                         'keep *_*_HGCalTBDWCTracks_*',
                                                                         'keep *_*_FullRunData_*')
)

process.source = cms.Source("HGCalTBGANSimSource",
                        fileNames=cms.untracked.vstring(["file:%s" % file for file in options.inputFiles]),
                        RechitOutputCollectionName = cms.string('HGCALTBRECHITS'), 
                        DWCOutputCollectionName = cms.string('DelayWireChambers'), 
                        RunDataOutputCollectionName = cms.string('FullRunData'), 
                        e_mapFile_CERN = cms.untracked.string(electronicMap),
                        MaskNoisyChannels=cms.untracked.bool(bool(options.MaskNoisyChannels)),
                        ChannelsToMaskFileName=cms.untracked.string(options.noisyChannelsFile),
                        beamEnergy=cms.untracked.uint32(options.beamEnergy),
                        beamParticlePDGID=cms.untracked.int32(options.beamParticlePDGID),                        
                        beamX_mu=cms.untracked.double(0.0),     #hard coded numbers, could be tuned
                        beamY_mu=cms.untracked.double(0.0),
                        beamX_sigma=cms.untracked.double(10.0),
                        beamY_sigma=cms.untracked.double(10.0),
                        setupConfiguration=cms.untracked.uint32(options.setupConfiguration),
                        areaSpecification = cms.untracked.string(options.areaSpecification),
                        GANModelIndex = cms.untracked.string(options.GANModelIndex),
                        NColorsInputImage = cms.untracked.uint32(options.NColorsInputImage),
                        NEvents = cms.untracked.uint32(options.NEvents),
                        zDim = cms.untracked.uint32(options.zDim),
                        wc_resolutions = cms.untracked.vdouble([0.2, 0.2, 0.2, 0.2])        #set to the expected resolutions according to the manual
                        )


process.dwctrackproducer = cms.EDProducer("DWCTrackProducer",
                                        MWCHAMBERS = cms.InputTag("source","DelayWireChambers" ), 
                                        OutputCollectionName=cms.string("HGCalTBDWCTracks"),
                                       layerPositionFile=cms.string(options.layerPositionFile)
)


####################################

process.p = cms.Path( process.dwctrackproducer )


process.end = cms.EndPath(process.output)