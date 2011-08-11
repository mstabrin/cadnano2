# Copyright 2011 Autodesk, Inc.  All rights reserved.
#
# The MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in 
# the Software without restriction, including without limitation the rights to 
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do 
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all 
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
# SOFTWARE.
#
# http://www.opensource.org/licenses/mit-license.php

"""
halfcylinderhelixnode.py

Created by Simon Breslav on 2011-08-04

A Maya Node for creating Half-Cylinder Helix Shape 
"""
import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import math

nodeName = "spHalfCylinderHelixNode"
id = OpenMaya.MTypeId(0x3114)


class HalfCylinderHelixNode(OpenMayaMPx.MPxNode):
    outputMesh = OpenMaya.MObject()
    startBaseAttr = OpenMaya.MObject()
    endBaseAttr = OpenMaya.MObject()
    totalBasesAttr = OpenMaya.MObject()       
    start3DPosAttr = OpenMaya.MObject()
    end3DPosAttr = OpenMaya.MObject()
    parityAttr = OpenMaya.MObject()        
    
    radiusAttr = OpenMaya.MObject()    
    rotationAttr = OpenMaya.MObject()
    riseAttr = OpenMaya.MObject()
    edgesPerBaseAttr = OpenMaya.MObject()    
    
    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)
        self.start3DPos = OpenMaya.MFloatPoint()
        self.end3DPos = OpenMaya.MFloatPoint()

    def compute(self, plug, data):
        try:      
            fnMeshData = OpenMaya.MFnMeshData()
            outMeshDataObj = fnMeshData.create()
            endData = data.inputValue(HalfCylinderHelixNode.endBaseAttr)
            startData = data.inputValue(HalfCylinderHelixNode.startBaseAttr)
            startVal = startData.asInt()
            endVal = endData.asInt()
            
            rotationData = data.inputValue(HalfCylinderHelixNode.rotationAttr)
            spacingData = data.inputValue(HalfCylinderHelixNode.riseAttr)
            edgesPerBaseData = data.inputValue(HalfCylinderHelixNode.edgesPerBaseAttr)
            radiusData = data.inputValue(HalfCylinderHelixNode.radiusAttr)
            totalNumBasesData = data.inputValue(HalfCylinderHelixNode.totalBasesAttr)
            totalNumBases = totalNumBasesData.asInt()
            parityData = data.inputValue(HalfCylinderHelixNode.parityAttr)
            parity = parityData.asInt()
            
            self.createMesh(startVal, endVal , totalNumBases, radiusData.asDouble(), rotationData.asDouble(), 
                            spacingData.asDouble(), 
                            edgesPerBaseData.asInt(),
                            parity, 
                            outMeshDataObj)   
                            
            startPosHandle = data.outputValue(HalfCylinderHelixNode.start3DPosAttr)
            startPosHandle.set3Float (self.start3DPos[0], self.start3DPos[1], self.start3DPos[2])
            endPosHandle = data.outputValue(HalfCylinderHelixNode.start3DPosAttr)
            endPosHandle.set3Float (self.end3DPos[0], self.end3DPos[1], self.end3DPos[2])
            
            handle = data.outputValue(HalfCylinderHelixNode.outputMesh)
            handle.setMObject(outMeshDataObj)
            handle.setClean()
            data.setClean(plug)
        except:
            print "Error in %s\n" % nodeName
            raise
        
    def createMesh(self, startVal, endVal, totalNumBases, radius, rotationAttr, riseAttr, edgesPerBase, parity, outData):
        # XXX [SB] start and end are inverted right now...
        middleBase = totalNumBases/2
        #print "startV endV %d %d %d" % (startVal, endVal, middleBase) 
        end = (middleBase-startVal)
        start = (endVal-middleBase)
        baseCount = start+end        
        numVerticesEnds = 20 
        numMiddleSections = int(baseCount*edgesPerBase)-1 #n
        #print "start %d end %d" % (start, end)
        rise = riseAttr/edgesPerBase  
        start_pos = -start * (riseAttr)
        numVerticesTotal = (numVerticesEnds * 2) + numMiddleSections*numVerticesEnds
        rot_ang = -rotationAttr / edgesPerBase 

        numFacesEnds = numVerticesEnds-2
        numFacesTotal = (numVerticesEnds-2)*2 +  (numVerticesEnds)* (numMiddleSections+1)
        numFaceConnects = ((numVerticesEnds-2) * 2 * 3) + (numVerticesEnds * (numMiddleSections+1) * 4)

        vtx = []
        rotation = 0
        starting_rotation = endVal * rotationAttr + (math.pi*parity)
        # Create Endpice verts       
        vtx.append( OpenMaya.MFloatPoint(0.0, start_pos, 0.0) )
        self.end3DPos = OpenMaya.MFloatPoint(0.0, start_pos, 0.0)         
        for i in range(1,numVerticesEnds):
            val = i*(180/(numFacesEnds))
            rad = (val*math.pi)/180
            vtx.append( OpenMaya.MFloatPoint( radius * math.cos(starting_rotation+rad), start_pos, radius*math.sin(starting_rotation+rad)) )
        # Create Middle verts
        for i in range(0,numMiddleSections):
            rotation = rot_ang * (i+1)
            pos = rise* (i+1)
            vtx.append( OpenMaya.MFloatPoint(0.0, start_pos+pos, 0.0) )                
            for i in range(1,numVerticesEnds):
                val = i*(180/(numFacesEnds))
                rad = (val*math.pi)/180
                #print "vrt %d, %f %f" % (i, val, rad) 
                x = radius * math.cos(starting_rotation+rad+rotation)
                y = radius*math.sin(starting_rotation+rad+rotation)     
                vtx.append( OpenMaya.MFloatPoint( x, start_pos+pos, y) )        

        # Create EndPiece verts
        vtx.append( OpenMaya.MFloatPoint(0.0, start_pos+(numMiddleSections+1)*rise, 0.0) )
        self.start3DPos = OpenMaya.MFloatPoint(0.0, start_pos+(numMiddleSections+1)*rise, 0.0)
        for i in range(1,numVerticesEnds):
            rotation = rot_ang * (1+numMiddleSections)
            val = i*(180/(numFacesEnds))
            rad = (val*math.pi)/180
            #print "vrt %d, %f %f" % (i, val, rad) 
            x = radius * math.cos(starting_rotation+rad+rotation)
            y = radius*math.sin(starting_rotation+rad+rotation)
            vtx.append( OpenMaya.MFloatPoint( x, start_pos+(numMiddleSections+1)*rise, y) )
        #print "vtx length %d"  % len(vtx)
        points = OpenMaya.MFloatPointArray()
        points.setLength(numVerticesTotal)

        for i in range(0,numVerticesTotal):
            points.set(vtx[i], i)

        faceConnects = OpenMaya.MIntArray()
        faceConnects.setLength(numFaceConnects)
        #print "numFaceConnects %d" % numFaceConnects
        offset = 1
        count = 0
        for i in range(0,numFacesEnds):
            faceConnects.set(0, count)
            count +=1
            faceConnects.set(offset, count)
            offset += 1
            count +=1
            faceConnects.set(offset, count)
            count +=1

        for k in range(0,numMiddleSections+1):
            for i in range(0, numVerticesEnds):
                if i < numVerticesEnds-1:
                    v1 = (k*numVerticesEnds)+i
                    v2 = (k*numVerticesEnds)+1+i
                    v3 = ((k+1)*numVerticesEnds)+i
                    v4 = ((k+1)*numVerticesEnds)+1+i
                else:
                    v1 = (k*numVerticesEnds)+i
                    v2 = (k*numVerticesEnds)
                    v3 = ((k+1)*numVerticesEnds)+i
                    v4 = ((k+1)*numVerticesEnds)

                faceConnects.set(v1, count)
                count +=1
                faceConnects.set(v2, count)
                count +=1
                faceConnects.set(v4, count)
                count +=1
                faceConnects.set(v3, count)
                count +=1

        offset = numVerticesTotal-numVerticesEnds+1
        for i in range(numFacesTotal-numFacesEnds, numFacesTotal):
            #print numVerticesTotal-numVerticesEnds
            #print offset 
            faceConnects.set(numVerticesTotal-numVerticesEnds, count)
            count +=1
            faceConnects.set(offset, count)
            offset += 1
            count +=1
            #print offset 
            faceConnects.set(offset, count)
            count +=1

        #print "face connect ended at %d" % count
        faceCounts = OpenMaya.MIntArray()
        faceCounts.setLength(numFacesTotal)
        count = 0
        for i in range(0,numFacesEnds):
            #print count            
            faceCounts.set(3, count)
            count += 1
        for i in range(numFacesEnds, numFacesTotal-numFacesEnds):
            #print count    
            faceCounts.set(4, count)
            count += 1
        for i in range(numFacesTotal-numFacesEnds, numFacesTotal):
            #print count    
            faceCounts.set(3, count)
            count += 1
        #print "face count ended at %d" % count
        meshFS = OpenMaya.MFnMesh()
        meshFS.create(numVerticesTotal, numFacesTotal, points, faceCounts, faceConnects, outData)

def nodeCreator():
    return OpenMayaMPx.asMPxPtr(HalfCylinderHelixNode())

def nodeInitialize():
    #unitAttr = OpenMaya.MFnUnitAttribute()
    typedAttr = OpenMaya.MFnTypedAttribute()
    HalfCylinderHelixNode.outputMesh = typedAttr.create("outputMesh",
                                                "out",
                                                OpenMaya.MFnData.kMesh)

    nAttr = OpenMaya.MFnNumericAttribute()

    HalfCylinderHelixNode.startBaseAttr = nAttr.create('startBase',
                                    'stb',
                                    OpenMaya.MFnNumericData.kInt,
                                    0)
    nAttr.setStorable(True)       
    HalfCylinderHelixNode.endBaseAttr = nAttr.create('endBase',
                                    'sab',
                                    OpenMaya.MFnNumericData.kInt,
                                    0)
    nAttr.setStorable(True)
    HalfCylinderHelixNode.totalBasesAttr = nAttr.create('totalBases',
                                    'tb',
                                    OpenMaya.MFnNumericData.kInt,
                                    0)
    nAttr.setStorable(True)
    
    HalfCylinderHelixNode.riseAttr = nAttr.create('rise',
                                    'r',
                                    OpenMaya.MFnNumericData.kDouble,
                                    0.34)
    nAttr.setMin(0.01)
    nAttr.setMax(1.0)
    nAttr.setStorable(True)
    HalfCylinderHelixNode.edgesPerBaseAttr = nAttr.create('edgesPerBase',
                                    'spb',
                                    OpenMaya.MFnNumericData.kInt,
                                    3)
    nAttr.setMin(1)
    nAttr.setMax(20)
    nAttr.setStorable(True)
    
    HalfCylinderHelixNode.radiusAttr = nAttr.create('radius',
                                    'rad',
                                    OpenMaya.MFnNumericData.kDouble,
                                    1.125)
    nAttr.setMin(1.0)
    nAttr.setMax(5.0)
    nAttr.setStorable(True)
    
    HalfCylinderHelixNode.parityAttr = nAttr.create('parity',
                                            'pa',
                                            OpenMaya.MFnNumericData.kInt,
                                            0)
    nAttr.setStorable(True)
    
    HalfCylinderHelixNode.start3DPosAttr = nAttr.create('startPos',
                                            'sp',
                                            OpenMaya.MFnNumericData.k3Float,
                                            0.0)
    #nAttr.setWritable(False)
    nAttr.setStorable(False)
    HalfCylinderHelixNode.end3DPosAttr = nAttr.create('endPos',
                                            'ep',
                                            OpenMaya.MFnNumericData.k3Float,
                                            0.0)
    #nAttr.setWritable(False)
    nAttr.setStorable(False)
    
    

    unitFn = OpenMaya.MFnUnitAttribute() 
    HalfCylinderHelixNode.rotationAttr = unitFn.create('rotation',
                                    'rot',
                                    OpenMaya.MFnUnitAttribute.kAngle,
                                    34.286 * math.pi / 180)
    unitFn.setMin(0.0)
    unitFn.setMax(math.pi)
    unitFn.setStorable(True)
    
    

    HalfCylinderHelixNode.addAttribute(HalfCylinderHelixNode.outputMesh)
    HalfCylinderHelixNode.addAttribute(HalfCylinderHelixNode.startBaseAttr)    
    HalfCylinderHelixNode.addAttribute(HalfCylinderHelixNode.endBaseAttr)
    HalfCylinderHelixNode.addAttribute(HalfCylinderHelixNode.totalBasesAttr)
    HalfCylinderHelixNode.addAttribute(HalfCylinderHelixNode.rotationAttr)
    HalfCylinderHelixNode.addAttribute(HalfCylinderHelixNode.riseAttr)
    HalfCylinderHelixNode.addAttribute(HalfCylinderHelixNode.edgesPerBaseAttr)
    HalfCylinderHelixNode.addAttribute(HalfCylinderHelixNode.start3DPosAttr)
    HalfCylinderHelixNode.addAttribute(HalfCylinderHelixNode.end3DPosAttr)
    HalfCylinderHelixNode.addAttribute(HalfCylinderHelixNode.radiusAttr)
    HalfCylinderHelixNode.addAttribute(HalfCylinderHelixNode.parityAttr)       
    
    HalfCylinderHelixNode.attributeAffects(HalfCylinderHelixNode.endBaseAttr, HalfCylinderHelixNode.outputMesh)
    HalfCylinderHelixNode.attributeAffects(HalfCylinderHelixNode.startBaseAttr, HalfCylinderHelixNode.outputMesh)
    HalfCylinderHelixNode.attributeAffects(HalfCylinderHelixNode.totalBasesAttr, HalfCylinderHelixNode.outputMesh)
    HalfCylinderHelixNode.attributeAffects(HalfCylinderHelixNode.rotationAttr, HalfCylinderHelixNode.outputMesh)
    HalfCylinderHelixNode.attributeAffects(HalfCylinderHelixNode.riseAttr, HalfCylinderHelixNode.outputMesh)
    HalfCylinderHelixNode.attributeAffects(HalfCylinderHelixNode.edgesPerBaseAttr, HalfCylinderHelixNode.outputMesh)
    HalfCylinderHelixNode.attributeAffects(HalfCylinderHelixNode.radiusAttr, HalfCylinderHelixNode.outputMesh)
    
    HalfCylinderHelixNode.attributeAffects(HalfCylinderHelixNode.endBaseAttr, HalfCylinderHelixNode.start3DPosAttr)
    HalfCylinderHelixNode.attributeAffects(HalfCylinderHelixNode.startBaseAttr, HalfCylinderHelixNode.start3DPosAttr)
    HalfCylinderHelixNode.attributeAffects(HalfCylinderHelixNode.totalBasesAttr, HalfCylinderHelixNode.start3DPosAttr)
    HalfCylinderHelixNode.attributeAffects(HalfCylinderHelixNode.riseAttr, HalfCylinderHelixNode.start3DPosAttr)
    HalfCylinderHelixNode.attributeAffects(HalfCylinderHelixNode.edgesPerBaseAttr, HalfCylinderHelixNode.start3DPosAttr)
    
    HalfCylinderHelixNode.attributeAffects(HalfCylinderHelixNode.endBaseAttr, HalfCylinderHelixNode.end3DPosAttr)
    HalfCylinderHelixNode.attributeAffects(HalfCylinderHelixNode.startBaseAttr, HalfCylinderHelixNode.end3DPosAttr)
    HalfCylinderHelixNode.attributeAffects(HalfCylinderHelixNode.totalBasesAttr, HalfCylinderHelixNode.end3DPosAttr)
    HalfCylinderHelixNode.attributeAffects(HalfCylinderHelixNode.riseAttr, HalfCylinderHelixNode.end3DPosAttr)
    HalfCylinderHelixNode.attributeAffects(HalfCylinderHelixNode.edgesPerBaseAttr, HalfCylinderHelixNode.start3DPosAttr)
   
    HalfCylinderHelixNode.attributeAffects(HalfCylinderHelixNode.outputMesh, HalfCylinderHelixNode.start3DPosAttr)
    HalfCylinderHelixNode.attributeAffects(HalfCylinderHelixNode.outputMesh, HalfCylinderHelixNode.end3DPosAttr)

def initializePlugin(obj):
    plugin = OpenMayaMPx.MFnPlugin(obj)

    try:
        plugin.registerNode(nodeName, id, nodeCreator, nodeInitialize)
    except:
        sys.stderr.write("Failed to register node %s\n" % nodeName)
        raise

def uninitializePlugin(obj):
    plugin = OpenMayaMPx.MFnPlugin(obj)

    try:
        plugin.deregisterNode(id)
    except:
        sys.stderr.write("Failed to deregister node %s\n" % nodeName)
        raise
