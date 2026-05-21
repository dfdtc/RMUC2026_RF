import crc
temp = []
with open("./test_decode.txt","rb") as doc:
    for line in doc.readlines():
        for b in line:
            temp.append(b)

rm_crc8 = crc.Configuration(8,0x31,0xff,0,True,True)
rm_crc16 = crc.Configuration(16,0x1021,0xffff,0,True,True)
header_crc_calc = crc.Calculator(rm_crc8,True)
frame_crc_calc = crc.Calculator(rm_crc16,True)

def bf_header_fixing(data_len,data,crc,fix_mode = "key"):
    data_temp = data
    DATA_LEN_RANGE = 64
    if data_len==1030:
        data_temp.insert(2,0)
        data_temp.pop()
        for i in range(255):
            data_temp[3] = i
            if header_crc_calc.checksum(bytes(data)) == crc:
                return data_temp
        return None
    
    if fix_mode == "key" and data_len == 6:
        for i in range(255):
            data_temp[3] = i
            if header_crc_calc.checksum(bytes(data)) == crc:
                return data_temp
        return None
    

    if data_len>DATA_LEN_RANGE:
        for i in range(65):
            data_temp[1] = i
            if header_crc_calc.checksum(bytes(data)) == crc:
                return data_temp
        return None
            

i = 0
header_broken = 0
frame_broken = 0
fully_fixed = 0
while i < len(temp):
    word = temp[i]
    #mark
    fix_header = False
    if word == 0xA5:
        i = i+1
        data_len = int.from_bytes(temp[i:i+2], byteorder='little')
        data_len_for_crc = temp[i:i+2]
        i = i+2
        seq = temp[i]
        i = i+1
        header_crc8 = temp[i]
        header_list = temp[i-4:i]
        if header_crc_calc.checksum(bytes(header_list)) != header_crc8:
            print("header crc error, trying to fix")
            #mark
            header_broken = header_broken + 1
            header_list = bf_header_fixing(data_len, header_list,header_crc8)
            if header_list == None:
                print("no bf result, won't fix")
                continue
            else:
                print("bf success, header fixed")
                fix_header = True
                data_len = int.from_bytes(header_list[1:3], byteorder='little')
                if data_len > 64:
                    print("data len too long, may be wrong")
                    continue
        header_list.append(header_crc8)
        
        i = i+1

        cmd = int.from_bytes(temp[i:i+3], byteorder='little')
        i = i+2
        data = temp[i:i+data_len]
        i = i+data_len
        frame_crc16 = int.from_bytes(temp[i:i+2], byteorder='little')
        frame_body = temp[i-data_len-2:i]
        frame = header_list+frame_body
        if frame_crc_calc.checksum(bytes(header_list+frame_body)) != frame_crc16:
            #mark
            frame_broken = frame_broken + 1
            
            print("frame crc error")
            continue
        i = i+2
        print(''.join(chr(i) for i in data))
        #mark
        if fix_header:
            fully_fixed = fully_fixed + 1
        continue
    
    i = i+1
#TODO: this module is not rubust enough, too much position moving action here
# it can not treat the case that frame is slice by the terminal of temp list(cause out of index error)
#希望失败的解码不要导致游标移动，避免意外的跳过太多数据（len_fix可能导致错误的data_len）
#基于概率的定位离群数据剔除，并插值恢复

print(f"header broken: {header_broken}, frame broken: {frame_broken}, fully fixed: {fully_fixed}")
        
        

