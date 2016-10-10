#!/usr/bin/env python
####################################################
##  VIVE2ANIM.py    1.0                           ##
##  HTC Vive logs to Maya .ANIM file converter    ##
##  Copyright (C) 2016 Walter Arrighetti, PhD     ##
##  All Rights Reserved.                          ##
####################################################
import math
import time
import sys
import os
import re

VERSION = "0.8"

vivere = re.compile(r"\[(?P<time>\S{23})\]\[(?P<lineidx>.{3})\]LogBlueprintUserMessages[:] \[(?P<controller>\S+)\](.*) Translation[:] X=(?P<dX>\S+) Y=(?P<dY>\S+) Z=(?P<dZ>\S+) Rotation: P=(?P<pitch>\S+) Y=(?P<yaw>\S+) R=(?P<roll>\S+) Scale X=(?P<scalX>\S+) Y=(?P<scalY>\S+) Z=(?P<scalZ>\S+)")
vivetimere = re.compile(r"(?P<yr>\d{4})[.](?P<mon>\d{2})[.](?P<day>\d{2})[-](?P<hh>\d{2})[.](?P<mm>\d{2})[.](?P<ss>\d{2})[:](?P<milli>\d{3})")
def vivetime(t):
	tre = vivetimere.match(t)
	return time.mktime(time.strptime(t[:19],"%Y.%m.%d-%H.%M.%S")) + float(tre.group('milli'))/1000


def sphere2rect(Rho, Theta, Phi, rad=True):
	if rad:	theta, phi = Theta, Phi
	else:	[theta, phi] = map(math.radians,[Theta,Phi])
	y = Rho * math.sin(theta) * math.sin(phi)
	x = Rho * math.sin(theta) * math.cos(phi)
	z = Rho * math.cos(theta)
	return (x, y, z)
def rect2sphere(x, y, z, rad=True):
	rho  = math.sqrt(math.pow(x,2.) + math.pow(y,2.) + math.pow(z,2.))
	Theta= math.acos(z/rho)
	Phi  = math.atan2(y,x)
	if rad:	theta, phi = Theta, Phi
	else:	[theta, phi] = map(math.degrees,[Theta,Phi])
	return (rho, theta, phi)
def RotationMatrix(Phi, Theta, Psi, order="xyz", rad=True):
	if rad:	phi, theta, psi = Phi, Theta, Psi
	else:	[phi, theta, psi] = map(math.radians,[Phi, Theta, Psi])
	if order.lower() in ["x","zxz","zxz'","zxzp"]:
		a11 = math.cos(psi)*math.cos(phi) - math.cos(theta)*math.sin(phi)*math.sin(psi)
		a12 = math.cos(psi)*math.sin(phi) + math.cos(theta)*math.cos(phi)*math.sin(psi)
		a13 = math.sin(psi)*math.sin(theta)
		a21 = -math.sin(psi)*math.cos(phi) - math.cos(theta)*math.sin(phi)*math.cos(psi)
		a22 = -math.sin(psi)*math.sin(phi) + math.cos(theta)*math.cos(phi)*math.cos(psi)
		a23 = math.cos(psi)*math.sin(theta)
		a31 = math.sin(theta)*math.sin(phi)
		a32 = -math.sin(theta)*math.cos(phi)
		a33 = math.cos(theta)
	elif order.lower() in ["y","yzx"]:
		a11 = math.cos(psi)*math.cos(phi) - math.cos(theta)*math.sin(phi)*math.sin(psi)
		a12 = math.cos(psi)*math.sin(phi) + math.cos(theta)*math.cos(phi)*math.sin(psi)
		a13 = math.sin(psi)*math.sin(theta)
		a21 = -math.sin(psi)*math.cos(phi) - math.cos(theta)*math.sin(phi)*math.cos(psi)
		a22 = -math.sin(psi)*math.sin(phi) + math.cos(theta)*math.cos(phi)*math.cos(psi)
		a23 = math.cos(psi)*math.sin(theta)
		a31 = math.sin(theta)*math.sin(phi)
		a32 = -math.sin(theta)*math.cos(phi)
		a33 = math.cos(theta)
	elif order.lower() in ["xyz","zyx","zy'x''","pitchrollyaw","pitch-roll-yaw","headingelevationbank","heading-elevation-bank"]:
		a11 = math.cos(theta)*math.cos(phi)
		a12 = math.cos(theta)*math.sin(phi)
		a13 = -math.sin(theta)
		a21 = math.sin(psi)*math.sin(theta)*math.cos(phi) - math.cos(psi)*math.sin(phi)
		a22 = math.sin(psi)*math.sin(theta)*math.sin(phi) + math.cos(psi)*math.cos(phi)
		a23 = math.cos(theta)*math.sin(psi)
		a31 = math.cos(psi)*math.sin(theta)*math.cos(phi) + math.sin(psi)*math.sin(phi)
		a32 = math.cos(psi)*math.sin(theta)*math.sin(phi) - math.sin(psi)*math.cos(phi)
		a33 = math.cos(theta)*math.cos(psi)
	else:	return ((0,0,0),(0,0,0),(0,0,0))
	return ((a11,a12,a13),(a21,a22,a23),(a31,a32,a33))


def main():
	animdata, time0 = [], None
	print "VIVE2ANIM - HTC Vive motion-log to Maya ANIM file converter %s"%VERSION
	print "Copyright (C) 2016 Walter Arrighetti <github.com/walter-arrighetti>"
	print "All Rights Reserved.\n"

	if len(sys.argv) not in [2,3]:
		print "Syntax: VIVE2ANIM  infile  [outfile]\n"
		sys.exit(9)
	VIVE_FILE = os.path.abspath(sys.argv[1])
	if len(sys.argv)==3:	ANIM_FILE = os.path.abspath(sys.argv[2])
	else:
		if VIVE_FILE.lower().endswith(".log") and len(os.path.basename(VIVE_FILE))>4:
			ANIM_FILE = os.path.basename(VIVE_FILE)[:-4] + ".anim"
		else:	ANIM_FILE = os.path.basename(VIVE_FILE) + ".anim"
	if not os.path.exists(VIVE_FILE):
		print " * ERROR!: Input file \"%s\" does not exist."%VIVE_FILE
		sys.exit(8)
	try:	fout = open(ANIM_FILE,"w")
	except:
		print " * ERROR!: Unable to write output file \"%s\"."%ANIM_FILE
		sys.exit(7)
	
	for key in animfiller.keys():
		for n in range(len(animfiller[key])):
			animfiller[key][n] = animfiller[key][n]+'\n'
	print " !! Remember !! - Y axis is *reflected*; the rotation axes ordering is 'YXZ',\n                  i.e. Roll first, then Pitch, then Yaw.\n"
	fout.writelines(animfiller['header'])
	
	with open(VIVE_FILE,"r") as fin:
		for line in fin:
			regic = vivere.match(line)
			if not regic:	continue
			now = vivetimere.match(regic.group('time'))
			if not now:	continue
			now = vivetime(regic.group('time'))
			if time0==None:	time0 = now
			else:	now = now-time0
			#rotsp = map(float,map(regic.group,['rho','theta','phi']))
			#rot = sphere2rect(rotsp[0], rotsp[1], rotsp[2], rad=False)
			rot = map(float,map(regic.group,['pitch','roll','yaw']))
			animdata.append({
				'idx' : int(regic.group('lineidx')),
				'dX'   : float(regic.group('dX')),
				'dY'   : -float(regic.group('dY')),
				'dZ'   : float(regic.group('dZ')),
				'pitch'  : float(regic.group('pitch')),
				'roll': float(regic.group('roll')),
				'yaw'  : float(regic.group('yaw')),
				'rotX' : rot[0],
				'rotY' : rot[1],
				'rotZ' : rot[2],
				'scalX': float(regic.group('scalX')),
				'scalY': float(regic.group('scalY')),
				'scalZ': float(regic.group('scalZ')),
				't'    : now,
				'ctrl' : regic.group('controller'),
				})
	time1 = animdata[-1]['t']
	duration = time1 #- time0
	fout.write("startTime 0;\n")
	#fout.write("endTime %f;\n"%duration)
	fout.write("endTime %d;\n"%(len(animdata)-1))

	for c in range(len(coords)):
		fout.writelines(animfiller[coords[c]])
		for n in xrange(len(animdata)):
			fout.writelines("    %d %f auto auto 1 0 0;\n"%(n,animdata[n][coords[c]]) )
		fout.writelines(animfiller['ender'])
		if coords[c]=='dZ':
			fout.writelines(animfiller['bridge'])
			for n in xrange(len(animdata)):
				fout.writelines("    %d %d auto auto 1 0 0;\n"%(n,1) )
			fout.writelines(animfiller['ender'])
	fout.writelines(animfiller['footer'])
	fout.close()
	print 'Vive log file "%s" converted into "%s" anim file.'%tuple(map(os.path.basename,[VIVE_FILE,ANIM_FILE]))


coords = ['dX','dY','dZ','rotX','rotY','rotZ','scalX','scalY','scalZ']
animfiller = {
	'header':"""animVersion 1.1;
mayaVersion 2017;
timeUnit pal;
linearUnit cm;
angularUnit deg;""".splitlines(),
	'footer':"""anim pCubeShape1 1 0 0;""".splitlines(),
	'dX':"""anim translate.translateX translateX pCube1 0 1 0;
animData {
  input time;
  output linear;
  weighted 1;
  preInfinity constant;
  postInfinity constant;
  keys {""".splitlines(),
	'dY':"""
anim translate.translateY translateY pCube1 0 1 1;
animData {
  input time;
  output linear;
  weighted 1;
  preInfinity constant;
  postInfinity constant;
  keys {""".splitlines(),
	'dZ':"""anim translate.translateZ translateZ pCube1 0 1 2;
animData {
  input time;
  output linear;
  weighted 1;
  preInfinity constant;
  postInfinity constant;
  keys {""".splitlines(),
	'rotX':"""anim rotate.rotateX rotateX pCube1 0 1 4;
animData {
  input time;
  output angular;
  weighted 1;
  preInfinity constant;
  postInfinity constant;
  keys {""".splitlines(),
	'rotY':"""anim rotate.rotateY rotateY pCube1 0 1 5;
animData {
  input time;
  output angular;
  weighted 1;
  preInfinity constant;
  postInfinity constant;
  keys {""".splitlines(),
	'rotZ':"""anim rotate.rotateZ rotateZ pCube1 0 1 6;
animData {
  input time;
  output angular;
  weighted 1;
  preInfinity constant;
  postInfinity constant;
  keys {""".splitlines(),
	'scalX':"""anim scale.scaleX scaleX pCube1 0 1 7;
animData {
  input time;
  output angular;
  weighted 1;
  preInfinity constant;
  postInfinity constant;
  keys {""".splitlines(),
	'scalY':"""anim scale.scaleY scaleY pCube1 0 1 8;
animData {
  input time;
  output angular;
  weighted 1;
  preInfinity constant;
  postInfinity constant;
  keys {""".splitlines(),
	'scalZ':"""anim scale.scaleZ scaleZ pCube1 0 1 9;
animData {
  input time;
  output angular;
  weighted 1;
  preInfinity constant;
  postInfinity constant;
  keys {""".splitlines(),
	'bridge':"""anim visibility visibility pCube1 0 1 3;
animData {
  input time;
  output unitless;
  weighted 1;
  preInfinity constant;
  postInfinity constant;
  keys {""".splitlines(),
	'ender':"""  }
}""".splitlines()
}


if __name__ == "__main__":
	main()
