Raw advertised services:

```
[NEW] Primary Service (Handle 0x72a1)
	/org/bluez/hci0/dev_E8_5B_5B_24_22_E4/service000a
	00001801-0000-1000-8000-00805f9b34fb
	Generic Attribute Profile
	[NEW] Characteristic (Handle 0x72a1) INDICATE? 0x20
		/org/bluez/hci0/dev_E8_5B_5B_24_22_E4/service000a/char000b
		00002a05-0000-1000-8000-00805f9b34fb
		Service Changed
		[NEW] Descriptor (Handle 0x98e4) CLIENT_CHARACTERISTIC_CONFIG_UUID / NOTIFCATION ?
			/org/bluez/hci0/dev_E8_5B_5B_24_22_E4/service000a/char000b/desc000d
			00002902-0000-1000-8000-00805f9b34fb
			Client Characteristic Configuration
[NEW] Primary Service (Handle 0x72a1) CONTROL
	/org/bluez/hci0/dev_E8_5B_5B_24_22_E4/service000e
	99fa0001-338a-1024-8a49-009c0215f78a
	Vendor specific
	[NEW] Characteristic (Handle 0x72a1) COMMAND 0x0c
		/org/bluez/hci0/dev_E8_5B_5B_24_22_E4/service000e/char000f
		99fa0002-338a-1024-8a49-009c0215f78a
		Vendor specific
	[NEW] Characteristic (Handle 0x72a1) ERROR 0x12
		/org/bluez/hci0/dev_E8_5B_5B_24_22_E4/service000e/char0011
		99fa0003-338a-1024-8a49-009c0215f78a
		Vendor specific
		[NEW] Descriptor (Handle 0xa514) CLIENT_CHARACTERISTIC_CONFIG_UUID / NOTIFCATION ?
			/org/bluez/hci0/dev_E8_5B_5B_24_22_E4/service000e/char0011/desc0013
			00002902-0000-1000-8000-00805f9b34fb
			Client Characteristic Configuration
[NEW] Primary Service (Handle 0x72a1) DPG
	/org/bluez/hci0/dev_E8_5B_5B_24_22_E4/service0014
	99fa0010-338a-1024-8a49-009c0215f78a
	Vendor specific
	[NEW] Characteristic (Handle 0x72a1) DPG  0x1e
		/org/bluez/hci0/dev_E8_5B_5B_24_22_E4/service0014/char0015
		99fa0011-338a-1024-8a49-009c0215f78a
		Vendor specific
		[NEW] Descriptor (Handle 0xae54) CLIENT_CHARACTERISTIC_CONFIG_UUID / NOTIFCATION ?
			/org/bluez/hci0/dev_E8_5B_5B_24_22_E4/service0014/char0015/desc0017
			00002902-0000-1000-8000-00805f9b34fb
			Client Characteristic Configuration
[NEW] Primary Service (Handle 0x72a1) REFERENCE_OUTPUT
	/org/bluez/hci0/dev_E8_5B_5B_24_22_E4/service0018
	99fa0020-338a-1024-8a49-009c0215f78a
	Vendor specific
	[NEW] Characteristic (Handle 0x72a1) ONE - NOTIFIES WHEN DESK MOVES 0x12
		/org/bluez/hci0/dev_E8_5B_5B_24_22_E4/service0018/char0019
		99fa0021-338a-1024-8a49-009c0215f78a
		Vendor specific
		[NEW] Descriptor (Handle 0xbc64) CLIENT_CHARACTERISTIC_CONFIG_UUID / NOTIFCATION ?
			/org/bluez/hci0/dev_E8_5B_5B_24_22_E4/service0018/char0019/desc001b
			00002902-0000-1000-8000-00805f9b34fb
			Client Characteristic Configuration
	[NEW] Characteristic (Handle 0x72a1) MASK 0x02
		/org/bluez/hci0/dev_E8_5B_5B_24_22_E4/service0018/char001c
		99fa0029-338a-1024-8a49-009c0215f78a
		Vendor specific
	[NEW] Characteristic (Handle 0x72a1) DETECT_MASK 0x02
		/org/bluez/hci0/dev_E8_5B_5B_24_22_E4/service0018/char001e
		99fa002a-338a-1024-8a49-009c0215f78a
		Vendor specific
[NEW] Primary Service (Handle 0x72a1) REFERENCE_INPUT
	/org/bluez/hci0/dev_E8_5B_5B_24_22_E4/service0020
	99fa0030-338a-1024-8a49-009c0215f78a
	Vendor specific
	[NEW] Characteristic (Handle 0x72a1) ONE 0x0c
		/org/bluez/hci0/dev_E8_5B_5B_24_22_E4/service0020/char0021
		99fa0031-338a-1024-8a49-009c0215f78a
		Vendor specific
```

My guess at what these are:

```
00002a05-0000-1000-8000-00805f9b34fb INDICATE? 0x20
99fa0002-338a-1024-8a49-009c0215f78a COMMAND 0x0c
99fa0003-338a-1024-8a49-009c0215f78a ERROR 0x12
99fa0011-338a-1024-8a49-009c0215f78a DPG 0x1e
99fa0021-338a-1024-8a49-009c0215f78a ONE (REFERENCE_OUTPUT) 0x12
99fa0029-338a-1024-8a49-009c0215f78a MASK 0x02
99fa002a-338a-1024-8a49-009c0215f78a DETECT_MASK 0x02
99fa0030-338a-1024-8a49-009c0215f78a ONE (REFERENCE_INPUT) 0x0c
```

Writing to the characteristices:

Writing to command takes little endian unsigned shorts  
Writing to Reference Input takes little endian signed shorts

```
import java.math.BigInteger;
// Code to convert the byte array declarations in the decompiled app to numbers
public class HelloWorld{

     /* Try this: */
    public static short byteArrayToShortLE(final byte[] b, final int offset)
    {
            short value = 0;
            for (int i = 0; i < 2; i++)
            {
                value |= (b[i + offset] & 0x000000FF) << (i * 8);
            }

            return value;
     }

     public static void main(String []args){
        byte[] b = new byte[]{-1, 127};
        int i = new BigInteger(b).intValue();
        System.out.println(byteArrayToShortLE(b, 0));
     }
}
```

Convert characteristic value:

```
raw = characteristic.read_value()
print("Inital height: {}".format(int.from_bytes(bytes([int(raw[0])]) + bytes([int(raw[1])]), 'little')))
```
