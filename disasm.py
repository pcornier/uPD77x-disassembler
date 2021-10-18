#!/usr/bin/python3.6

import argparse

def main():

  help = '''
uPD777 Disassembler.
This is based on Oguchi's design note document. The bit numbering starts with 1 as in the original document.
You can choose between physical or LSFR order for the disassembly with the -d option, default is LSFR.
  '''

  parser = argparse.ArgumentParser(description=help, formatter_class=argparse.RawTextHelpFormatter)
  required = parser.add_argument_group('required arguments:')
  required.add_argument('-i', '--input', help='input file', required=True)
  required.add_argument('-o', '--output', help='output file', required=True)
  parser.add_argument('-d', '--order', nargs='?', type=str, default='lsfr', help='phy or lsfr')
  args = parser.parse_args()

  with open(args.output, 'w') as outfile:

    romfile = open(args.input, 'rb')
    romdata = bytes(romfile.read())
    romfile.close()
    
    listing = {}

    for i in range(0, len(romdata), 2):
      b = (romdata[i] << 8 | romdata[i+1]) & 0xfff
      addr = i >> 1

      row = ''
      row = row + '%003X\t%003X' % (addr, b)
      
      op = 'unknown opcode'
      if b == 0:
        op = 'NOP'
      elif b == 0x4:
        op = 'GPL, skip if GunPortLatch = 1'
      elif b == 0x8:
        op = 'H->NRM'
      elif b == 0x18:
        op = 'H<->X'
      elif b == 0x20:
        op = 'SRE'
      elif b == 0x28 or b == 0x29:
        op = '(STB<<1|{0})->STB'.format(b&1)
      
      elif b == 0x49:
        op = '4H BLK, skip if 4H HBlank'
      elif b == 0x4a:
        op = 'VBLK, skip if VBlank'
      elif b == 0x4c:
        op = 'GPSW/, skip if GP&SW/ input = 1'

      elif b == 0x54:
        op = 'A->MA'
      elif b == 0x58:
        op = 'MA->A'
      elif b == 0x5C:
        op = 'MA<->A'

      elif b == 0x60:
        op = 'SRE+1'

      elif b == 0x30:
        op = 'PD1, skip if 1'
      elif b == 0x34:
        op = 'PD2, skip if 1'
      elif b == 0x38:
        op = 'PD3, skip if 1'
      elif b == 0x3c:
        op = 'PD4, skip if 1'

      elif b == 0x70:
        op = 'PD1, skip if 0'
      elif b == 0x74:
        op = 'PD2, skip if 0'
      elif b == 0x78:
        op = 'PD3, skip if 0'
      elif b == 0x7c:
        op = 'PD4, skip if 0'

      elif b >= 0x80 and b <= 0xff:
        op = 'M-{0:02X}, skip if borrow'.format(b&31)

      elif b >= 0x100 and b <= 0x17f:
        op = 'M+{0:02X}->M {1}->L, skip if carry'.format(b&31, (b>>5)&3)
      elif b >= 0x180 and b <= 0x1ff:
        op = 'M-{0:02X}->M {1}->L, skip if borrow'.format(b&31, (b>>5)&3)

      elif b >= 0x480 and b <= 0x49f:
        op = 'H-{0:02X}->H, skip if borrow'.format(b&31)
      elif b >= 0x4c0 and b <= 0x4df:
        op = 'H-{0:02X}->H, skip if carry'.format(b&31)

      elif b >= 0x210 and b <= 0x213:
        op = 'A1·A2 {0}->L, skip if A1&A2 makes zero'.format(b&3)
      elif b >= 0x230 and b <= 0x233:
        op = 'A1·A2 {0}->L, skip if A1&A2 makes non zero'.format(b&3)
      elif b >= 0x218 and b <= 0x21b:
        op = 'A1=A2 {0}->L, skip if A1-A2 makes zero'.format(b&3)
      elif b >= 0x238 and b <= 0x23b:
        op = 'A1=A2 {0}->L, skip if A1-A2 makes non zero'.format(b&3)
      elif b >= 0x21c and b <= 0x21f:
        op = 'A1-A2 {0}->L, skip if A1-A2 makes borrow'.format(b&3)
      elif b >= 0x23c and b <= 0x23f:
        op = 'A1-A2 {0}->L, skip if A1-A2 makes non borrow'.format(b&3)

      elif b >= 0x240 and b <= 0x243:
        op = 'A2·A1 {0}->L, skip if A2&A1 makes zero'.format(b&3)
      elif b >= 0x260 and b <= 0x263:
        op = 'A2·A1 {0}->L, skip if A2&A1 makes non zero'.format(b&3)
      elif b >= 0x248 and b <= 0x24b:
        op = 'A2=A1 {0}->L, skip if A2-A1 makes zero'.format(b&3)
      elif b >= 0x268 and b <= 0x26b:
        op = 'A2=A1 {0}->L, skip if A2-A1 makes non zero'.format(b&3)
      elif b >= 0x24c and b <= 0x24f:
        op = 'A2-A1 {0}->L, skip if A2-A1 makes borrow'.format(b&3)
      elif b >= 0x26c and b <= 0x26f:
        op = 'A2-A1 {0}->L, skip if A2-A1 makes non borrow'.format(b&3)

      elif b >= 0x280 and b <= 0x283:
        op = 'M·A1 {0}->L, skip if M&A1 makes zero'.format(b&3)
      elif b >= 0x2a0 and b <= 0x2a3:
        op = 'M·A1 {0}->L, skip if M&A1 makes non zero'.format(b&3)
      elif b >= 0x288 and b <= 0x28b:
        op = 'M=A1 {0}->L, skip if M-A1 makes zero'.format(b&3)
      elif b >= 0x2a8 and b <= 0x2ab:
        op = 'M=A1 {0}->L, skip if M-A1 makes non zero'.format(b&3)
      elif b >= 0x28c and b <= 0x28f:
        op = 'M-A1 {0}->L, skip if M-A1 makes borrow'.format(b&3)
      elif b >= 0x2ac and b <= 0x2af:
        op = 'M-A1 {0}->L, skip if M-A1 makes non borrow'.format(b&3)

      elif b >= 0x290 and b <= 0x293:
        op = 'M·A2 {0}->L, skip if M&A2 makes zero'.format(b&3)
      elif b >= 0x2b0 and b <= 0x2b3:
        op = 'M·A2 {0}->L, skip if M&A2 makes non zero'.format(b&3)
      elif b >= 0x298 and b <= 0x29b:
        op = 'M=A2 {0}->L, skip if M-A2 makes zero'.format(b&3)
      elif b >= 0x2b8 and b <= 0x2bb:
        op = 'M=A2 {0}->L, skip if M-A2 makes non zero'.format(b&3)
      elif b >= 0x29c and b <= 0x29f:
        op = 'M-A2 {0}->L, skip if M-A2 makes borrow'.format(b&3)
      elif b >= 0x2bc and b <= 0x2bf:
        op = 'M-A2 {0}->L, skip if M-A2 makes non borrow'.format(b&3)

      elif b >= 0x2c0 and b <= 0x2c3:
        op = 'H·A1 {0}->L, skip if H&A1 makes zero'.format(b&3)
      elif b >= 0x2e0 and b <= 0x2e3:
        op = 'H·A1 {0}->L, skip if H&A1 makes non zero'.format(b&3)
      elif b >= 0x2c8 and b <= 0x2cb:
        op = 'H=A1 {0}->L, skip if H-A1 makes zero'.format(b&3)
      elif b >= 0x2e8 and b <= 0x2eb:
        op = 'H=A1 {0}->L, skip if H-A1 makes non zero'.format(b&3)
      elif b >= 0x2cc and b <= 0x2cf:
        op = 'H-A1 {0}->L, skip if H-A1 makes borrow'.format(b&3)
      elif b >= 0x2ec and b <= 0x2ef:
        op = 'H-A1 {0}->L, skip if H-A1 makes non borrow'.format(b&3)

      elif b >= 0x2d0 and b <= 0x2d3:
        op = 'H·A2 {0}->L, skip if H&A2 makes zero'.format(b&3)
      elif b >= 0x2f0 and b <= 0x2f3:
        op = 'H·A2 {0}->L, skip if H&A2 makes non zero'.format(b&3)
      elif b >= 0x2d8 and b <= 0x2db:
        op = 'H=A2 {0}->L, skip if H-A2 makes zero'.format(b&3)
      elif b >= 0x2f8 and b <= 0x2fb:
        op = 'H=A2 {0}->L, skip if H-A2 makes non zero'.format(b&3)
      elif b >= 0x2dc and b <= 0x2df:
        op = 'H-A2 {0}->L, skip if H-A2 makes borrow'.format(b&3)
      elif b >= 0x2fc and b <= 0x2ff:
        op = 'H-A2 {0}->L, skip if H-A2 makes non borrow'.format(b&3)

      elif b >= 0x300 and b <= 0x303:
        op = '{0}->L'.format(b&3)

      elif b == 0x308:
        op = 'A1->FLS 0->L'
      elif b == 0x309:
        op = 'A1->FRS 1->L'
      elif b >= 0x30a and b <= 0x30b:
        op = 'A1->MODE 1{0}->L'.format(b&1)
      elif b >= 0x318 and b <= 0x31b:
        op = 'A1->RS {0}->L'.format(b&3)

      elif b == 0x348:
        op = 'A2->FLS 0->L'
      elif b == 0x349:
        op = 'A2->FRS 1->L'
      elif b >= 0x34a and b <= 0x34b:
        op = 'A2->MODE 1{0}->L'.format(b&1)
      elif b >= 0x358 and b <= 0x35b:
        op = 'A2->RS {0}->L'.format(b&3)

      elif b == 0x388:
        op = 'M->FLS 0->L'
      elif b == 0x389:
        op = 'M->FRS 1->L'
      elif b >= 0x38a and b <= 0x38b:
        op = 'M->MODE 1{0}->L'.format(b&1)
      elif b >= 0x398 and b <= 0x39b:
        op = 'M->RS {0}->L'.format(b&3)

      elif b >= 0x330 and b <= 0x333:
        op = 'A1·A2->A1 {0}->L'.format(b&3)
      elif b >= 0x334 and b <= 0x337:
        op = 'A1+A2->A1 {0}->L'.format(b&3)
      elif b >= 0x338 and b <= 0x33b:
        op = 'A1|A2->A1 {0}->L'.format(b&3)
      elif b >= 0x33c and b <= 0x33f:
        op = 'A1-A2->A1 {0}->L, skip if borrow'.format(b&3)

      elif b >= 0x360 and b <= 0x363:
        op = 'A2·A1->A2 {0}->L'.format(b&3)
      elif b >= 0x364 and b <= 0x367:
        op = 'A2+A1->A2 {0}->L'.format(b&3)
      elif b >= 0x368 and b <= 0x36b:
        op = 'A2|A1->A2 {0}->L'.format(b&3)
      elif b >= 0x36c and b <= 0x36f:
        op = 'A2-A1->A2 {0}->L, skip if borrow'.format(b&3)

      elif b >= 0x380 and b <= 0x383:
        op = 'A1->M {0}->L'.format(b&3)
      elif b >= 0x390 and b <= 0x393:
        op = 'A2->M {0}->L'.format(b&3)
      elif b >= 0x384 and b <= 0x387:
        op = 'M<->A1 {0}->L'.format(b&3)
      elif b >= 0x394 and b <= 0x397:
        op = 'M<->A2 {0}->L'.format(b&3)
      elif b >= 0x38c and b <= 0x38f:
        op = 'M->A1 {0}->L'.format(b&3)
      elif b >= 0x39c and b <= 0x39f:
        op = 'M->A2 {0}->L'.format(b&3)

      elif b >= 0x3b0 and b <= 0x3b3:
        op = 'M·A2->M {0}->L'.format(b&3)
      elif b >= 0x3b4 and b <= 0x3b7:
        op = 'M+A2->M {0}->L, skip if carry'.format(b&3)
      elif b >= 0x3b8 and b <= 0x3bb:
        op = 'M|A2->M {0}->L'.format(b&3)
      elif b >= 0x3bc and b <= 0x3bf:
        op = 'M-A2->M {0}->L, skip if borrow'.format(b&3)

      elif b >= 0x3a0 and b <= 0x3a3:
        op = 'M·A1->M {0}->L'.format(b&3)
      elif b >= 0x3a4 and b <= 0x3a7:
        op = 'M+A1->M {0}->L, skip if carry'.format(b&3)
      elif b >= 0x3a8 and b <= 0x3ab:
        op = 'M|A1->M {0}->L'.format(b&3)
      elif b >= 0x3ac and b <= 0x3af:
        op = 'M-A1->M {0}->L, skip if borrow'.format(b&3)

      elif b >= 0x3c0 and b <= 0x3c3:
        op = 'A1->H {0}->L'.format(b&3)
      elif b >= 0x3d0 and b <= 0x3d3:
        op = 'A2->H {0}->L'.format(b&3)
      elif b >= 0x3cc and b <= 0x3cf:
        op = 'H->A1 {0}->L'.format(b&3)
      elif b >= 0x3dc and b <= 0x3df:
        op = 'H->A2 {0}->L'.format(b&3)

      elif b == 0x400 or b == 0x401:
        op = '{0}->A11'.format(b&1)
      elif b == 0x402 or b == 0x403:
        op = 'JPM, 0->L, {0}->A11'.format(b&1)
      elif b >= 0x440 and b <= 0x47d:
        op = 'DGKS {0:b} (N={1})'.format((b>>2)&15, b&1)

      elif b >= 0x500 and b <= 0x57f:
        op = '{0:03X}->M[H,L]'.format(b&127)
      elif b >= 0x580 and b <= 0x5ff:
        op = '{0}->L, {1:03X}->H'.format((b>>5)&3, b&127)

      elif b >= 0x600 and b <= 0x67f:
        op = '{0:03X}->A1'.format(b&127)
      elif b >= 0x680 and b <= 0x6ff:
        op = '{0:03X}->A2'.format(b&127)
      elif b >= 0x700 and b <= 0x77f:
        op = '{0:03X}->A3'.format(b&127)
      elif b >= 0x780 and b <= 0x7ff:
        op = '{0:03X}->A4'.format(b&127)
        
      elif b >= 0x800 and b <= 0xbff:
        op = 'JP {0:03X}'.format(b&1023)
      elif b >= 0xc00 and b <= 0xfff:
        op = 'JS {0:03X}'.format(b&1023)
      
      pcnext = (addr&1920) | ((addr&63)<<1) | ((addr>>5)&1 == (addr>>6)&1)
      
      row = row + '\t' + op
      row = row + '\n'

      listing[addr] = (row, pcnext)
    
    if args.order == 'lsfr':
      outfile.write(listing.get(0)[0])
      for item in listing.items():
        if (listing.get(item[1][1])):
          outfile.write(listing.get(item[1][1])[0])
    else:
      for item in listing.items():
        outfile.write(item[1][0])

    outfile.close()

if __name__ == '__main__':
  main()

