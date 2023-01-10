/*
Esta macro preprocesa los datos, convirtiendo los ficheros .txt recién copiados a pnfs en un fichero root para facilitar el análisis.
*/

#include <TTimer.h>
#include <fstream>
#include <iostream>
#include <TH1D.h>
#include <TFile.h>
#include <TMath.h>
#include <TTree.h>
#include <TBranch.h>
#include <TLine.h>
#include <TCanvas.h>

#include <sstream>      // std::istringstream

#include"lib/InputConfig.h"
#include"lib/FirstDataProcess.h"


// vector<int> sc = {6};
// vector<int> sipms = {0,1};
// vector<int> pmt = {4};
// vector<int> pmtsipm = {0,1,4};

void FirstDataProcess(string input = "../input/config_file_firstdataprocess.txt")
{ /* Función principal de esta macro. Las direfentes funciones _Input() llaman al archivo de configuracion e importan las variables pertinentes */

  /////////////////////////////////////////////////////////////////////
  //___AQUI SE IMPORTAN LAS VARIABLES DEL ARCHIVO DE CONFIGURACIÓN___//
  /////////////////////////////////////////////////////////////////////  
  
  int irun; int frun; std::vector<int> channels;
  irun = IntInput(input, "I_RUN"); frun = IntInput(input, "F_RUN"); channels = IntVectorInput(input, "CHANNEL");

  string inputpath; string outputpath;
  inputpath = StringInput(input, "IPATH"); outputpath = StringInput(input, "OPATH");

  //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
  //___LAS VARIABLES QUE SE HAN IMPORTADO SE PASAN A LA FUNCIÓN ANALYSE QUE A SU VEZ LLAMA AL RUN_T PERTINENTE Y EJECUTA LAS FUNCIONES ESCOGIDAS___//  
  //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

  for (int run=irun; run<=frun; run++) for (int ch:channels) ReadAndDumpBinaryWindows(inputpath+Form("/wave%i.dat",ch),outputpath+Form("run%02i_ch%i.root",run,ch));
  /*  0.  Path de la carpeta que incluye los archivos .dat del ADC
	    1.  Path de la carpeta que incluye los archivos .root leidos
  */
}

