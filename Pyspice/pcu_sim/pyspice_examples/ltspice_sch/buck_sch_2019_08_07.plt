[Transient Analysis]
{
   Npanes: 2
   {
      traces: 2 {524290,0,"V(n002)"} {34603011,1,"I(R4)"}
      X: ('m',1,0,0.0001,0.001)
      Y[0]: (' ',0,0,1,10)
      Y[1]: (' ',1,-0.1,0.1,1.5)
      Volts: (' ',0,0,1,0,1,10)
      Amps: (' ',0,0,1,-0.1,0.1,1.5)
      Log: 0 0 0
      GridStyle: 1
   },
   {
      traces: 1 {34603012,0,"I(L1)"}
      X: ('m',1,0,0.0001,0.001)
      Y[0]: (' ',1,-0.2,0.2,2.4)
      Y[1]: (' ',1,1e+308,0.5,-1e+308)
      Amps: (' ',0,0,1,-0.2,0.2,2.4)
      Log: 0 0 0
      GridStyle: 1
   }
}
