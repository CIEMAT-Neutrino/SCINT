// --------------------------------------------------------------------------------- //
// ----------- Macro to process raw data from the lab to get .root files ----------- //
// --------------------------------------------------------------------------------- //


//#include "mylib.h"
//#include"Event.h"
//#include"Cuts.h"
//#include"Run.h"
#include <fstream>
#include "lib.h"
#include "Waveform.h"

using namespace std;
void lets_pause()
{
  TTimer *timer = new TTimer("gSystem->ProcessEvents();", 50, kFALSE);
  timer->TurnOn();
  timer->Reset();
  std::cout << "q/Q to quit, other to continuee: ";
  char kkey;
  std::cin.get(kkey);
  if (kkey == 'q' || kkey == 'Q') { throw std::exception(); } // std::exit(0); //gSystem->Exit(0); //
  timer->TurnOff();
  delete timer;
} //End lets_pause

int lets_pause(int &counter)
{
  TTimer *timer = new TTimer("gSystem->ProcessEvents();", 50, kFALSE);
  timer->TurnOn();
  timer->Reset();
  std::cout << "q/Q to quit, r to go back to last item, p to print and keep going, other to not print and keep going.";
  char kkey;
  std::cin.get(kkey);
  if (kkey == 'q' || kkey == 'Q') { throw std::exception(); } // std::exit(0); //gSystem->Exit(0); //
  if (kkey == 'r' || kkey == 'R') { counter = counter - 2; }
  timer->TurnOff();
  delete timer;
  if (kkey == 'P' || kkey == 'p') { return 1; }
  else { return 0; }
} //End lets_pause

class Waveform_t
{
  unsigned int Length;
  int BoardID;
  int Channel;
  int EventNumber;
  ULong64_t TriggerTimeStamp;
  ULong64_t PCTimeStamp = 0;
  double Sampling;
  // DCoffset

  public:
    std::vector<short> ADCs;
    std::vector<short> GetADCs() { return ADCs; }
    std::vector<double> ADCd;
    std::vector<double> GetADCd() { return ADCd; }
    ULong64_t GetTriggerTimeStamp() { return TriggerTimeStamp; }
    ULong64_t GetPCTimeStamp() { return PCTimeStamp; }
    int GetEventNumber() { return EventNumber; }
    double GetSampling() { return Sampling; }

  bool LoadBinary(unsigned int len, int EN, ULong64_t triggtstmp, vector<int> adc, int pol = -1)
  {
    Length = len;
    EventNumber = EN;
    TriggerTimeStamp = triggtstmp;
    PCTimeStamp = triggtstmp * 0.000000008; // Unidades de TriggerTimeStamp *0.000000008;
    for (auto amp : adc)
      if (pol == -1) ADCs.push_back(amp);
      else ADCs.push_back(-amp+16384);  // Para leer la SC por su polaridad positiva
    
    return true;
  }
  bool Load(ifstream *ifs, bool DEBUG = false, bool TS = false)
  {
    string s;
    getline(*ifs, s);
    if (DEBUG) cout << s << endl; // Record Length: 3072
    if (ifs->eof()) return false;
    s = s.substr(15, s.length() - 15);
    Length = stoi(s);
    if (DEBUG) cout << "Length: " << Length << endl; // lets_pause();
    getline(*ifs, s);
    if (DEBUG) cout << s << endl; // BoardID: 0
    getline(*ifs, s);
    if (DEBUG) cout << s << endl; // Channel: 0
    getline(*ifs, s);
    if (DEBUG) cout << s << endl; // Event Number: 57776
    s = s.substr(14, s.length() - 14);
    EventNumber = stoi(s);
    if (DEBUG) cout << "EventNumber: " << EventNumber << endl;
    getline(*ifs, s);
    if (DEBUG) cout << s << endl; // Pattern: 0x0000
    getline(*ifs, s);
    if (DEBUG) { cout << s << endl; } // Trigger Time Stamp: 3004795797  2756456643
    s = s.substr(20, s.length() - 20);
    TriggerTimeStamp = stol(s);
    if (DEBUG) cout << "TriggerTimeStamp: " << TriggerTimeStamp << endl;
    getline(*ifs, s);
    if (DEBUG) cout << s << endl; // DC offset (DAC): 0x0CCC
    if (TS)
    {
      getline(*ifs, s);
      s = s.substr(14, s.length() - 14);
      PCTimeStamp = stol(s);
      if (DEBUG) cout << "PC TriggerTimeStamp: " << PCTimeStamp << endl; // PC TriggerTimeStamp: 1594803786
      getline(*ifs, s);
      if (DEBUG) cout << s << endl; // ComputerTime Format 2: Wed Jul 15 11:03:06 2020
      getline(*ifs, s);
      if (DEBUG) cout << s << endl; // DC offset (DAC): 0x0CCC  // lets_pause();
    }

    for (unsigned int i = 0; i < Length; i++)
    {
      getline(*ifs, s);
      if (DEBUG) cout << i << " " << s << endl;
      if (s == "")
      {
        return false;
        if (DEBUG) cout << "File CUT, end run here" << endl;
      }
      ADCs.push_back(stoi(s));
      if (DEBUG) cout << " OK" << endl;
    }
    if (DEBUG) cout << "ADC samples " << ADCs.size() << " " << Length << endl;
    
    return true;
  }

  bool LoadOscilloscope(TString file, bool DEBUG = false, unsigned int Length = 52)
  {
    ifstream ifs;
    ifs.open(file);
    if (DEBUG) { cout << file << endl; };
    TString Line1, Line2, Line3, Line4, Line5, Line6;
    ifs >> Line1;
    if (DEBUG) cout << "1 " << Line1 << endl;
    ifs >> Line2;
    if (DEBUG) cout << "2 " << Line2 << endl;
    ifs >> Line3;
    if (DEBUG) cout << "3 " << Line3 << endl;
    ifs >> Line4;
    if (DEBUG) cout << "4 " << Line4 << endl;
    ifs >> Line5;
    if (DEBUG) cout << "5 " << Line5 << endl;
    ifs >> Line6;
    if (DEBUG) cout << "6 " << Line6 << endl;
    
    for (unsigned int j = 0; j < Length; j++)
    {
      double time, adc;
      char c;
      ifs >> time >> c >> adc;
      ADCd.push_back(adc);
      // if(DEBUG) cout << j << " " << adc<<endl;
      if (j == 0) Sampling = time;
      if (j == 1) Sampling = time - Sampling;
    }
    if (DEBUG) cout << "ADC samples " << ADCd.size() << " " << Length << endl;
    if (DEBUG) cout << "Sampling " << Sampling << endl;
    
    return true;
  }
  /*
  LECROYHDO9404,30152,Waveform
  Segments,1,SegmentSize,502
  Segment,TrigTime,TimeSinceSegment1
  #1,28-Dec-2020 13:34:10,0
  Time,Ampl
  -1.78051e-07,-0.00034916992
  -1.76051e-07,-0.00029708659
  -1.74051e-07,-0.00029708659
  -1.72051e-07,-0.00035812174
  -1.70051e-07,-0.00042729492
  */
}; //End class definition

void Dump(std::vector<Waveform_t> *w, string file, bool Osci = false)
{
  TFile f(file.c_str(), "RECREATE");
  TTree *t = new TTree("IR02", "IR02");
  std::vector<double> _ud;
  std::vector<short> _us;
  int _EventNumber;
  ULong64_t _TriggerTimeStamp;
  ULong64_t _PCTimeStamp;
  double _Sampling;

  TBranch  *_bn_u;
  if (Osci) _bn_u = t->Branch("ADC", &_ud);
  else      _bn_u = t->Branch("ADC", &_us);
 
  TBranch *_bn_Sampling    = t->Branch("Sampling", &_Sampling);
  TBranch *_bn_EventNumber = t->Branch("EventNumber", &_EventNumber);
  TBranch *_bn_PCTimeStamp = t->Branch("PCTimeStamp", &_PCTimeStamp);
  TBranch *_bn_TriggerTimeStamp = t->Branch("TriggerTimeStamp", &_TriggerTimeStamp);
  
  for (unsigned int i = 0; i < w->size(); i++)
  {
    if (Osci) _ud = w->at(i).GetADCd();
    else      _us = w->at(i).GetADCs();
    _EventNumber = w->at(i).GetEventNumber();
    _TriggerTimeStamp = w->at(i).GetTriggerTimeStamp();
    _PCTimeStamp = w->at(i).GetPCTimeStamp();
    _Sampling = w->at(i).GetSampling();
    t->Fill();
  }
  t->Write("IR02");
  f.Close();
  cout << "Dumped to file " << file << endl
       << endl;
} //End Dump

void Draw(std::vector<double> *w)
{
  TH1D *h = new TH1D("h", "h", w->size(), 0, w->size());
  for (unsigned int j = 0; j < w->size(); j++)
    h->SetBinContent(j + 1, w->at(j));
  h->Draw("HIST");
  lets_pause();
} //End Draw

void Draw(std::vector<short> *w)
{
  TH1D *h = new TH1D("h", "h", w->size(), 0, w->size());
  for (unsigned int j = 0; j < w->size(); j++) h->SetBinContent(j + 1, w->at(j));
  h->Draw("HIST");
  lets_pause();
}//End Draw

TH1D *GetTH1(std::vector<double> *w)
{
  TH1D *h = new TH1D("h", ";Time(ns);ADC", w->size(), 0, 4 * w->size());
  for (unsigned int j = 0; j < w->size(); j++) h->SetBinContent(j + 1, w->at(j));  // h->Draw("HIST"); lets_pause();
  
  return h;
} //End GetTH1

TH1D *GetTH1(std::vector<short> *w)
{
  TH1D *h = new TH1D("h", ";Time(ns);ADC", w->size(), 0, 4 * w->size());
  for (unsigned int j = 0; j < w->size(); j++) h->SetBinContent(j + 1, w->at(j)); // h->Draw("HIST"); lets_pause();
  
  return h;
} //End GetTH1

TH1D *GetAverage(string file, string title)
{
  TFile f(file.c_str(), "READ");
  TTree *t = (TTree *)f.Get("IR02");
  std::vector<double> *w = NULL;
  t->SetBranchAddress("ADC", &w);
  t->GetEntry(0);
  cout << w->size() << endl;
  TH1D *myh = GetTH1(w); // myh->Draw("HIST"); lets_pause();
  for (unsigned int i = 1; i < t->GetEntries(); i++)
  {
    t->GetEntry(i);       // cout << w->size() << endl;
    TH1D *h1 = GetTH1(w); // h1->Draw("HIST"); lets_pause();
    myh->Add(h1);
  }
  myh->Scale(1.0 / t->GetEntries());
  myh->SetTitle(title.c_str());
  
  return myh;
} //End GetAverage

void Load(std::vector<string> file, std::vector<string> name)
{
  ana::EventReader_t ev;
  for (unsigned int i = 0; i < file.size(); i++) ev.SetFile(file[i], name[i]);
  for (unsigned int j = 0; j < 100; j++)
  {
    ev.Draw(j);
    lets_pause();
  }
} //End Load

int ReadAndDump(string file, string outfile, bool TS = false)
{
  int nevents = -1;
  cout << "Loading " << file << endl;
  ifstream ifs;
  ifs.open(file);

  if (ifs.is_open())
  {
    cout << "File opened." << endl;

    std::vector<Waveform_t> wv;
    int i = 0;
    bool debug = false;
    while (!ifs.eof())
    {
      Waveform_t w0;
      bool b;
      b = w0.Load(&ifs, debug, TS);
      if (b)
      {
        if (debug) Draw(&(w0.ADCs));
        wv.push_back(w0);
        if (i == 0) cout << "Wvf length: " << wv[0].ADCs.size() << " samples." << endl;
        i++;
      }
      if (i % 5000 == 0) cout << "Loaded waveform " << i << endl;
    }
    cout << "Loaded " << wv.size() << " waveforms from " << file << endl;
    cout << "Wvf length: " << wv[0].ADCs.size() << " samples." << endl;
    cout << "Run duration: " << 1.0 * (wv[wv.size() - 1].GetTriggerTimeStamp() - wv[0].GetTriggerTimeStamp()) / 60.0 << " min." << endl;
    cout << "Data Rate: " << 1.0 * wv.size() / (wv[wv.size() - 1].GetTriggerTimeStamp() - wv[0].GetTriggerTimeStamp()) << " Hz." << endl;

    cout << "PCTS Run duration: " << 1.0 * (wv[wv.size() - 1].GetPCTimeStamp() - wv[0].GetPCTimeStamp()) / 60.0 << " min." << endl;
    cout << "PCTS Data Rate: " << 1.0 * wv.size() / (wv[wv.size() - 1].GetPCTimeStamp() - wv[0].GetPCTimeStamp()) << " Hz." << endl;

    nevents = wv.size();
    Dump(&wv, outfile);
    wv.clear();
  }

  else cout << "Failed to open file." << endl;
  
  return nevents;
} //End ReadAndDump

//************************* Funcion para leer binario ******************
int ReadAndDumpBinary(string file, string outfile)
{
  int nevents = -1;
  const char *input = file.c_str();

  FILE *pFile;
  const int HeaderLines = 6;
  uint32_t filehd[HeaderLines];
  uint32_t ChSize;
  string titles[HeaderLines] = {"EventSize", "BoardId", "ChannelMask", "EventCounter", "ExtendedTTT", "TriggerTimeTag"};
  unsigned int PrevEvent = -1;
  pFile = fopen(input, "rb");
  std::vector<Waveform_t> wv;
  int i = 0;
  cout << "Loading " << file << endl;
  if (pFile != NULL) cout << "File opened." << endl;
  else cout << "Failed to open file." << endl;
  while (1)
  {
    if (pFile != NULL)
    {
      Waveform_t w0;

      fread(filehd, sizeof(uint32_t), sizeof(filehd) / sizeof(uint32_t), pFile);
      // when we read last event, it repeats, so we stop the loop
      if (PrevEvent == filehd[3]) break;
      else PrevEvent = filehd[3];

      int NumSamples = (filehd[0] / 2) - (HeaderLines * 2);
      uint16_t samples[NumSamples];
      fread(samples, sizeof(uint16_t), sizeof(samples) / sizeof(uint16_t), pFile);
      vector<int> smp;
      for (auto a : samples) smp.push_back(a);
      bool b = w0.LoadBinary(NumSamples, PrevEvent, (filehd[5] + filehd[4] * pow(2, 32)), smp);
      wv.push_back(w0);
    }
    else break;
    if (wv.size() % 10000 == 0) cout << "Loaded waveform " << wv.size() << endl;   // break; // just if we want to read a fixed number of waveforms
  }
  fclose(pFile);

  cout << "Loaded " << wv.size() << " waveforms from " << file << endl;
  cout << "Wvf length: " << wv[0].ADCs.size() << " samples." << endl;
  cout << "Run duration: " << 1.0 * (wv[wv.size() - 1].GetTriggerTimeStamp() * 0.000000008 - wv[0].GetTriggerTimeStamp() * 0.000000008) / 60.0 << " min." << endl;
  cout << "Data Rate: " << 1.0 * wv.size() / (wv[wv.size() - 1].GetTriggerTimeStamp() * 0.000000008 - wv[0].GetTriggerTimeStamp() * 0.000000008) << " Hz." << endl;
  cout << "PCTS Run duration: " << 1.0 * (wv[wv.size() - 1].GetPCTimeStamp() - wv[0].GetPCTimeStamp()) / 60.0 << " min." << endl;
  cout << "PCTS Data Rate: " << 1.0 * wv.size() / (wv[wv.size() - 1].GetPCTimeStamp() - wv[0].GetPCTimeStamp()) << " Hz." << endl;
  nevents = wv.size();
  Dump(&wv, outfile, false);
  wv.clear();

  return nevents;
} // End ReadAndDumpBinary

int ReadAndDumpBinaryWindows(string file, string outfile)
{
  int nevents = -1;
  const char *input = file.c_str();

  FILE *pFile;
  const int HeaderLines = 6;
  uint32_t filehd[HeaderLines];
  uint32_t ChSize;
  string titles[HeaderLines] = {"EventSize", "BoardId", "ChannelMask", "EventCounter", "ExtendedTTT", "TriggerTimeTag"}; // , "DCOffset"
  // unsigned int PrevEvent = -1;
  unsigned int TimeStamp = -1;
  pFile = fopen(input, "rb");
  std::vector<Waveform_t> wv;
  int i = 0;
  cout << "Loading " << file << endl;
  if (pFile != NULL) cout << "File opened." << endl;
  else cout << "Failed to open file." << endl;
  while (1)
  {
    if (pFile != NULL)
    {
      Waveform_t w0;
      // cout << "Sizeof filhhd: " << sizeof(filehd) << endl;
      fread(filehd, sizeof(uint32_t), sizeof(filehd) / sizeof(uint32_t), pFile);
      // when we read last event, it repeats, so we stop the loop
      // if (PrevEvent == filehd[3] && PrevEvent!=0)
      if (TimeStamp == filehd[5])  
      {
        cout << "FIN!" << endl;
        break;
      }
      else
      {
        TimeStamp = filehd[5];
        i++;
      };

      int NumSamples = (filehd[0] / 2) - (HeaderLines * 2);
      // int NumSamples = 250;
      uint16_t samples[NumSamples];
      fread(samples, sizeof(uint16_t), sizeof(samples) / sizeof(uint16_t), pFile);
      // fread(samples, sizeof(uint32_t), sizeof(samples) / sizeof(uint32_t), pFile);
      vector<int> smp;
      for (auto a : samples) smp.push_back(a);
      bool b = w0.LoadBinary(NumSamples, i, (filehd[5]), smp,1);
      wv.push_back(w0);
      // for (auto n=0; n<HeaderLines;n++) cout << filehd[n] << endl;
    }
    else break;
    if (wv.size() % 10000 == 0) cout << "Loaded waveform " << wv.size() << endl;
  }

  fclose(pFile);

  cout << "Loaded " << wv.size() << " waveforms from " << file << endl;
  cout << "Wvf length: " << wv[0].ADCs.size() << " samples." << endl;
  cout << "Run duration: " << 1.0 * (wv[wv.size() - 1].GetTriggerTimeStamp() * 0.000000008 - wv[0].GetTriggerTimeStamp() * 0.000000008) / 60.0 << " min." << endl;
  cout << "Data Rate: " << 1.0 * wv.size() / (wv[wv.size() - 1].GetTriggerTimeStamp() * 0.000000008 - wv[0].GetTriggerTimeStamp() * 0.000000008) << " Hz." << endl;
  cout << "PCTS Run duration: " << 1.0 * (wv[wv.size() - 1].GetPCTimeStamp() - wv[0].GetPCTimeStamp()) / 60.0 << " min." << endl;
  cout << "PCTS Data Rate: " << 1.0 * wv.size() / (wv[wv.size() - 1].GetPCTimeStamp() - wv[0].GetPCTimeStamp()) << " Hz." << endl;
  nevents = wv.size();
  Dump(&wv, outfile, false);
  wv.clear();

  return nevents;
} //End ReadAndDumpBinaryWindows

int ReadAndDumpBinaryLight(string file, string outfile)
{
  int nevents = -1;
  const char *input = file.c_str();

  FILE *pFile;
  const int HeaderLines = 6;
  uint32_t filehd[HeaderLines];
  uint32_t ChSize;
  string titles[HeaderLines] = {"EventSize", "BoardId", "ChannelMask", "EventCounter", "ExtendedTTT", "TriggerTimeTag"};
  unsigned int PrevEvent = -1;
  pFile = fopen(input, "rb");
  int i = 0;
  cout << "Loading " << file << endl;
  if (pFile != NULL) cout << "File opened." << endl;
  else cout << "Failed to open file." << endl;

  TFile f(outfile.c_str(), "RECREATE");
  f.cd();
  TTree *t = new TTree("IR02", "IR02");
  std::vector<short> _u;
  int _EventNumber;
  ULong64_t _TriggerTimeStamp;
  ULong64_t _PCTimeStamp;

  TBranch *_bn_u = t->Branch("ADC", &_u);
  TBranch *_bn_EventNumber = t->Branch("EventNumber", &_EventNumber);
  TBranch *_bn_TriggerTimeStamp = t->Branch("TriggerTimeStamp", &_TriggerTimeStamp);
  TBranch *_bn_PCTimeStamp = t->Branch("PCTimeStamp", &_PCTimeStamp);
  int counter = 0;
  while (1)
  {
    if (pFile != NULL)
    {
      Waveform_t w0;

      fread(filehd, sizeof(uint32_t), sizeof(filehd) / sizeof(uint32_t), pFile);
      // when we read last event, it repeats, so we stop the loop
      if (PrevEvent == filehd[3]) break;
      else PrevEvent = filehd[3];

      int NumSamples = (filehd[0] / 2) - (HeaderLines * 2);
      uint16_t samples[NumSamples];
      fread(samples, sizeof(uint16_t), sizeof(samples) / sizeof(uint16_t), pFile);
      vector<int> smp;
      for (auto a : samples) smp.push_back(a);
      bool b = w0.LoadBinary(NumSamples, PrevEvent, (filehd[5] + filehd[4] * pow(2, 32)), smp);
      _u = w0.GetADCs();
      _EventNumber = w0.GetEventNumber();
      _TriggerTimeStamp = w0.GetTriggerTimeStamp();
      _PCTimeStamp = w0.GetPCTimeStamp();
      t->Fill();
      counter++;
    }
    else break;
    if (counter % 20000 == 0) cout << "Loaded waveform " << counter << endl;   //~ if(wv.size()%100000==0){ cout << "Loaded waveform " << wv.size()<< endl;break;}
  }

  fclose(pFile);

  //  cout << "Loaded " << counter << " waveforms from " << file << endl;
  //  cout << "Wvf length: " << wv[0].ADCs.size() << " samples." << endl;
  //  cout << "Run duration: " << 1.0*(wv[wv.size()-1].GetTriggerTimeStamp()-wv[0].GetTriggerTimeStamp())/60.0 << " min." << endl;
  //  cout << "Data Rate: " << 1.0*wv.size()/(wv[wv.size()-1].GetTriggerTimeStamp()-wv[0].GetTriggerTimeStamp()) << " Hz." << endl;
  //  cout << "PCTS Run duration: " << 1.0*(wv[wv.size()-1].GetPCTimeStamp()-wv[0].GetPCTimeStamp())/60.0 << " min." << endl;
  //  cout << "PCTS Data Rate: " << 1.0*wv.size()/(wv[wv.size()-1].GetPCTimeStamp()-wv[0].GetPCTimeStamp()) << " Hz." << endl;
  //  nevents=wv.size();

  t->Write("IR02");
  f.Close();
  cout << "Dumped to file " << file << endl
       << endl;

  return nevents;
} //End ReadAndDumpBinaryLight

int evt_Length(string file)
{
  // cout<<files_path<<endl;
  int Length = 0;
  TString Line1, Line2;
  string Line3;
  ifstream fd1;
  fd1.open(file);
  fd1 >> Line1;
  cout << Line1 << endl;
  Line2.ReadToDelim(fd1, ',');
  cout << Line2 << endl;
  Line2.ReadToDelim(fd1, ',');
  cout << Line2 << endl;
  Line2.ReadToDelim(fd1, ',');
  cout << Line2 << endl;
  Line2.ReadToDelim(fd1, ',');
  cout << Line2 << endl;
  Line3 = Line2.Data();
  Length = stoi(Line3);
  cout << "Length: " << Length << endl; // lets_pause();
  fd1.close();

  return Length;
} //End evt_Length

int ReadAndDumpOscilloscope(string file, string outfile, int nevents = -1)
{
  cout << "Loading " << file + "00001.txt" << endl;
  ifstream ifs;
  int Length = evt_Length(file + "00001.txt");
  cout << Length << endl;
  ifs.open(file + "00001.txt");
  if (ifs.is_open())
  {
    cout << "File opened." << endl;
    std::vector<Waveform_t> wv;
    int i = 1;
    bool debug = false;
    while (ifs.is_open())
    {
      ifstream ifs2;
      string file2 = Form("%s%05i.txt", file.c_str(), i);
      if (debug) cout << "Loading file " << file2 << endl;
      ifs.close();
      ifs.open(file2);
      if (!ifs.is_open()) continue;
      
      Waveform_t w0;
      bool myb = w0.LoadOscilloscope(file2, debug, Length);
      if (myb)
      {
        if (debug)
          Draw(&(w0.ADCd));
        wv.push_back(w0);
        if (i == 0)
          cout << "Wvf length: " << wv[0].ADCd.size() << " samples." << endl;
        i++;
      }
      if (i % 5000 == 0) cout << "Loaded waveform " << i << endl;
    }

    cout << "Loaded " << wv.size() << " waveforms from " << file << " - Samping: " << wv[0].GetSampling() << endl;
    cout << "Wvf length: " << wv[0].ADCd.size() << " samples." << endl;
    cout << "Run duration: " << 1.0 * (wv[wv.size() - 1].GetTriggerTimeStamp() - wv[0].GetTriggerTimeStamp()) / 60.0 << " min." << endl;
    cout << "Data Rate: " << 1.0 * wv.size() / (wv[wv.size() - 1].GetTriggerTimeStamp() - wv[0].GetTriggerTimeStamp()) << " Hz." << endl;
    cout << "PCTS Run duration: " << 1.0 * (wv[wv.size() - 1].GetPCTimeStamp() - wv[0].GetPCTimeStamp()) / 60.0 << " min." << endl;
    cout << "PCTS Data Rate: " << 1.0 * wv.size() / (wv[wv.size() - 1].GetPCTimeStamp() - wv[0].GetPCTimeStamp()) << " Hz." << endl;
    nevents = wv.size();
    Dump(&wv, outfile, true);
    wv.clear();
  }
  else cout << "Failed to open file." << endl;

  return nevents;
} //End ReadAndDumpOscilloscope