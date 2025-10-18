# EncodingExplosion
A tool let you know you file encoding.

# USAGE
### INTRO
```py
BinPrint(file,size=-1)

EncodingExplosion(tbin)

EncodingExplosionFile(file,size=-1)

AutoDetect(file,size=-1)   # pip install chardet
```
## DETAILS
```ps
PS C:\Users\原神\Desktop> python

Python 3.13.7 (tags/v3.13.7:bcee1c3, Aug 14 2025, 14:15:11) [MSC v.1944 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.

>>> import EncodingExplosion

>>> EncodingExplosion.BinPrint(r"C:\TEST\VMD-Lifting-master\VMD-Lifting-master\applications\2.vmd",256)
b'Vocaloid Motion Data 0002\x00\x00\x00\x00\x00Dummy Model Name    \x8d\x0e\x00\x00\x8f\xe3\x94\xbc\x90g\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc0\xff\x00\x00\xc0\xff\x00\x00\xc0\xff\x00\x00\xc0\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x89\xba\x94\xbc\x90g\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc0\xff\x00\x00\xc0\xff\x00\x00\xc0\xff\x00\x00\xc0\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

>>> EncodingExplosion.EncodingExplosion(b"\xc0\xff\x00\x00\xc0\xff\x00\x00\xc0\xff\x00\x00\xc0\xff")
ascii
     error
big5
     error
big5hkscs
     error
cp037
     {{{{
cp273
     ääää
cp424
     {{{{
cp437
     └ └ └ └ 
cp500
     {{{{
cp720
     └ └ └ └ 
cp737
     └ └ └ └ 
cp775
     └ └ └ └ 
cp850
     └ └ └ └ 
cp852
     └ └ └ └ 
cp855
     └ └ └ └ 
cp856
     └ └ └ └ 
cp857
     └ └ └ └ 
cp858
     └ └ └ └ 
cp860
     └ └ └ └ 
cp861
     └ └ └ └ 
cp862
     └ └ └ └ 
cp863
     └ └ └ └ 
cp864
     error
cp865
     └ └ └ └ 
cp866
     └ └ └ └ 
cp869
     └ └ └ └ 
cp874
     error
cp875
     {{{{
cp932
     ﾀﾀﾀﾀ
cp949
     error
cp950
     error
cp1006
     ﭺﹽﭺﹽﭺﹽﭺﹽ
cp1026
     çççç
cp1125
     └ └ └ └ 
cp1140
     {{{{
cp1250
     Ŕ˙Ŕ˙Ŕ˙Ŕ˙
cp1251
     АяАяАяАя
cp1252
     ÀÿÀÿÀÿÀÿ
cp1253
     error
cp1254
     ÀÿÀÿÀÿÀÿ
cp1255
     error
cp1256
     ہےہےہےہے
cp1257
     Ą˙Ą˙Ą˙Ą˙
cp1258
     ÀÿÀÿÀÿÀÿ
euc_jp
     error
euc_jis_2004
     error
euc_jisx0213
     error
euc_kr
     error
gb2312
     error
gbk
     error
gb18030
     error
hz
     error
iso2022_jp
     error
iso2022_jp_1
     error
iso2022_jp_2
     error
iso2022_jp_2004
     error
iso2022_jp_3
     error
iso2022_jp_ext
     error
iso2022_kr
     error
latin_1
     ÀÿÀÿÀÿÀÿ
iso8859_2
     Ŕ˙Ŕ˙Ŕ˙Ŕ˙
iso8859_3
     À˙À˙À˙À˙
iso8859_4
     Ā˙Ā˙Ā˙Ā˙
iso8859_5
     РџРџРџРџ
iso8859_6
     error
iso8859_7
     error
iso8859_8
     error
iso8859_9
     ÀÿÀÿÀÿÀÿ
iso8859_10
     ĀĸĀĸĀĸĀĸ
iso8859_11
     error
iso8859_13
     Ą’Ą’Ą’Ą’
iso8859_14
     ÀÿÀÿÀÿÀÿ
iso8859_15
     ÀÿÀÿÀÿÀÿ
iso8859_16
     ÀÿÀÿÀÿÀÿ
johab
     error
koi8_r
     юЪюЪюЪюЪ
koi8_t
     юЪюЪюЪюЪ
koi8_u
     юЪюЪюЪюЪ
kz1048
     АяАяАяАя
mac_cyrillic
     ј€ј€ј€ј€
mac_greek
     ά­ά­ά­ά­
mac_iceland
     ¿ˇ¿ˇ¿ˇ¿ˇ
mac_latin2
     ņˇņˇņˇņˇ
mac_roman
     ¿ˇ¿ˇ¿ˇ¿ˇ
mac_turkish
     ¿ˇ¿ˇ¿ˇ¿ˇ
ptcp154
     АяАяАяАя
shift_jis
     error
shift_jis_2004
     error
shift_jisx0213
     error
utf_32
     error
utf_32_be
     error
utf_32_le
     error
utf_16
     ￀￀￀￀
utf_16_be
     샿샿샿샿
utf_16_le
     ￀￀￀￀
utf_7
     error
utf_8
     error
utf_8_sig
     error


>>> EncodingExplosion.EncodingExplosionFile(r"C:\TEST\VMD-Lifting-master\VMD-Lifting-master\applications\2.vmd",256)
ascii
     error
big5
     error
big5hkscs
     error
cp037
     î?Ä/%?ÑÀ(?ÈÑ?>à/È/àÍ__`(?ÀÁ%+/_Áý±Tm¯°Å{{{{i[m¯°Å{{{{
cp273
     î?[/%?ÑÀ(?ÈÑ?>à/È/àÍ__`(?ÀÁ%+/_Áý±Tm‾°Åääääi¬m‾°Åääää
cp424
     error
cp437
     Vocaloid Motion Data 0002Dummy Model Name    ìÅπö╝Ég└ └ └ └ ë║ö╝Ég└ └ └ └ 
cp500
     î?Ä/%?ÑÀ(?ÈÑ?>à/È/àÍ__`(?ÀÁ%+/_Áý±Tm¯°Å{{{{i¬m¯°Å{{{{
cp720
     Vocaloid Motion Data 0002Dummy Model Name    ع¤╝g└ └ └ └ ë║¤╝g└ └ └ └ 
cp737
     Vocaloid Motion Data 0002Dummy Model Name    ΞΠήΦ╝Ρg└ └ └ └ Κ║Φ╝Ρg└ └ └ └ 
cp775
     Vocaloid Motion Data 0002Dummy Model Name    ŹÅŃö╝Ég└ └ └ └ ē║ö╝Ég└ └ └ └ 
cp850
     Vocaloid Motion Data 0002Dummy Model Name    ìÅÒö╝Ég└ └ └ └ ë║ö╝Ég└ └ └ └ 
cp852
     Vocaloid Motion Data 0002Dummy Model Name    ŹĆŃö╝Ég└ └ └ └ ë║ö╝Ég└ └ └ └ 
cp855
     Vocaloid Motion Data 0002Dummy Model Name    ЇЈсћ╝љg└ └ └ └ Ѕ║ћ╝љg└ └ └ └ 
cp856
     error
cp857
     Vocaloid Motion Data 0002Dummy Model Name    ıÅÒö╝Ég└ └ └ └ ë║ö╝Ég└ └ └ └ 
cp858
     Vocaloid Motion Data 0002Dummy Model Name    ìÅÒö╝Ég└ └ └ └ ë║ö╝Ég└ └ └ └ 
cp860
     Vocaloid Motion Data 0002Dummy Model Name    ìÂπõ╝Ég└ └ └ └ Ê║õ╝Ég└ └ └ └ 
cp861
     Vocaloid Motion Data 0002Dummy Model Name    ÞÅπö╝Ég└ └ └ └ ë║ö╝Ég└ └ └ └ 
cp862
     Vocaloid Motion Data 0002Dummy Model Name    םןπפ╝נg└ └ └ └ י║פ╝נg└ └ └ └ 
cp863
     Vocaloid Motion Data 0002Dummy Model Name    ‗§πË╝Ég└ └ └ └ ë║Ë╝Ég└ └ └ └ 
cp864
     error
cp865
     Vocaloid Motion Data 0002Dummy Model Name    ìÅπö╝Ég└ └ └ └ ë║ö╝Ég└ └ └ └ 
cp866
     Vocaloid Motion Data 0002Dummy Model Name    НПуФ╝Рg└ └ └ └ Й║Ф╝Рg└ └ └ └ 
cp869
     error
cp874
     error
cp875
     Ο?Υ/%?ΫΦ(? Ϋ?>Δ/ /ΔΊ__`(?ΦΧ%+/_ΧδζTmυ°Ω{{{{iςmυ°Ω{{{{
cp932
     error
cp949
     error
cp950
     error
cp1006
     Vocaloid Motion Data 0002Dummy Model Name    ﻙﺙgﭺﹽﭺﹽﭺﹽﭺﹽﭦﺙgﭺﹽﭺﹽﭺﹽﭺﹽ
cp1026
     î?Ä/%?ÑÀ(?ÈÑ?>à/È/àÍ__ı(?ÀÁ%+/_Á`±Tm¯°Åççççi¬m¯°Åçççç
cp1125
     Vocaloid Motion Data 0002Dummy Model Name    НПуФ╝Рg└ └ └ └ Й║Ф╝Рg└ └ └ └ 
cp1140
     î?Ä/%?ÑÀ(?ÈÑ?>à/È/àÍ__`(?ÀÁ%+/_Áý±Tm¯°Å{{{{i[m¯°Å{{{{
cp1250
     error
cp1251
     Vocaloid Motion Data 0002Dummy Model Name    ЌЏг”јђgАяАяАяАя‰є”јђgАяАяАяАя
cp1252
     error
cp1253
     error
cp1254
     error
cp1255
     error
cp1256
     Vocaloid Motion Data 0002Dummy Model Name    چڈم”¼گgہےہےہےہے‰؛”¼گgہےہےہےہے
cp1257
     error
cp1258
     error
euc_jp
     error
euc_jis_2004
     error
euc_jisx0213
     error
euc_kr
     error
gb2312
     error
gbk
     error
gb18030
     error
hz
     error
iso2022_jp
     error
iso2022_jp_1
     error
iso2022_jp_2
     error
iso2022_jp_2004
     error
iso2022_jp_3
     error
iso2022_jp_ext
     error
iso2022_kr
     error
latin_1
     Vocaloid Motion Data 0002Dummy Model Name    ã¼gÀÿÀÿÀÿÀÿº¼gÀÿÀÿÀÿÀÿ
iso8859_2
     Vocaloid Motion Data 0002Dummy Model Name    ăźgŔ˙Ŕ˙Ŕ˙Ŕ˙şźgŔ˙Ŕ˙Ŕ˙Ŕ˙
iso8859_3
     error
iso8859_4
     Vocaloid Motion Data 0002Dummy Model Name    ãŧgĀ˙Ā˙Ā˙Ā˙ēŧgĀ˙Ā˙Ā˙Ā˙
iso8859_5
     Vocaloid Motion Data 0002Dummy Model Name    уМgРџРџРџРџКМgРџРџРџРџ
iso8859_6
     error
iso8859_7
     error
iso8859_8
     error
iso8859_9
     Vocaloid Motion Data 0002Dummy Model Name    ã¼gÀÿÀÿÀÿÀÿº¼gÀÿÀÿÀÿÀÿ
iso8859_10
     Vocaloid Motion Data 0002Dummy Model Name    ãžgĀĸĀĸĀĸĀĸšžgĀĸĀĸĀĸĀĸ
iso8859_11
     error
iso8859_13
     Vocaloid Motion Data 0002Dummy Model Name    ć¼gĄ’Ą’Ą’Ą’ŗ¼gĄ’Ą’Ą’Ą’
iso8859_14
     Vocaloid Motion Data 0002Dummy Model Name    ãỳgÀÿÀÿÀÿÀÿẃỳgÀÿÀÿÀÿÀÿ
iso8859_15
     Vocaloid Motion Data 0002Dummy Model Name    ãŒgÀÿÀÿÀÿÀÿºŒgÀÿÀÿÀÿÀÿ
iso8859_16
     Vocaloid Motion Data 0002Dummy Model Name    ăŒgÀÿÀÿÀÿÀÿșŒgÀÿÀÿÀÿÀÿ
johab
     error
koi8_r
     Vocaloid Motion Data 0002Dummy Model Name    █▐Ц■╪░gюЪюЪюЪюЪ┴╨■╪░gюЪюЪюЪюЪ
koi8_t
     error
koi8_u
     Vocaloid Motion Data 0002Dummy Model Name    █▐Ц■╪░gюЪюЪюЪюЪ┴╨■╪░gюЪюЪюЪюЪ
kz1048
     Vocaloid Motion Data 0002Dummy Model Name    ҚЏг”әђgАяАяАяАя‰ғ”әђgАяАяАяАя
mac_cyrillic
     Vocaloid Motion Data 0002Dummy Model Name    НПгФЉРgј€ј€ј€ј€ЙЇФЉРgј€ј€ј€ј€
mac_greek
     Vocaloid Motion Data 0002Dummy Model Name    çèψîΦêgά­ά­ά­ά­âΚîΦêgά­ά­ά­ά­
mac_iceland
     Vocaloid Motion Data 0002Dummy Model Name    çè„îºêg¿ˇ¿ˇ¿ˇ¿ˇâ∫îºêg¿ˇ¿ˇ¿ˇ¿ˇ
mac_latin2
     Vocaloid Motion Data 0002Dummy Model Name    ćŹ„ĒľźgņˇņˇņˇņˇČļĒľźgņˇņˇņˇņˇ
mac_roman
     Vocaloid Motion Data 0002Dummy Model Name    çè„îºêg¿ˇ¿ˇ¿ˇ¿ˇâ∫îºêg¿ˇ¿ˇ¿ˇ¿ˇ
mac_turkish
     Vocaloid Motion Data 0002Dummy Model Name    çè„îºêg¿ˇ¿ˇ¿ˇ¿ˇâ∫îºêg¿ˇ¿ˇ¿ˇ¿ˇ
ptcp154
     Vocaloid Motion Data 0002Dummy Model Name    ҚҸг”јҗgАяАяАяАяүә”јҗgАяАяАяАя
shift_jis
     error
shift_jis_2004
     error
shift_jisx0213
     error
utf_32
     error
utf_32_be
     error
utf_32_le
     error
utf_16
     潖慣潬摩䴠瑯潩⁮慄慴〠〰2畄浭⁹潍敤⁬慎敭††ຍ범析쀀ÿ쀀ÿ쀀ÿ쀀ÿ褀钺邼g￀￀￀￀
utf_16_be
     噯捡汯楤⁍潴楯渠䑡瑡‰〰㈀䑵浭礠䵯摥氠乡浥††贎迣钼遧À＀À＀À＀À＀몔벐最샿샿샿샿
utf_16_le
     潖慣潬摩䴠瑯潩⁮慄慴〠〰2畄浭⁹潍敤⁬慎敭††ຍ범析쀀ÿ쀀ÿ쀀ÿ쀀ÿ褀钺邼g￀￀￀￀
utf_7
     error
utf_8
     error
utf_8_sig
     error

>>> # pip install chardet

>>> EncodingExplosion.AutoDetect(r"C:\TEST\VMD-Lifting-master\VMD-Lifting-master\applications\2.vmd")
{'encoding': None, 'confidence': 0.0, 'language': None}

>>> EncodingExplosion.AutoDetect(r"10161050.pdf",2**12)
{'encoding': 'Windows-1252', 'confidence': 0.6230172413793104, 'language': ''}
>>> exit()

PS C:\Users\原神\Desktop>

```