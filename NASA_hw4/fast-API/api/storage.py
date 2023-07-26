import base64
import hashlib
import sys
import os
from pathlib import Path
from typing import List, Any

import schemas
from config import settings
from fastapi import UploadFile
from fastapi import HTTPException, status
from loguru import logger
from pydantic import ValidationError
#from app import APP

def remove_all(self, filename:str):
    for i in range(0, settings.NUM_DISKS):
        filepath=str(self.block_path[i])+"/"+filename
        if os.path.exists(filepath):
            os.remove(filepath)

class Storage:
    def __init__(self, is_test: bool):
        self.block_path: List[Path] = [
            Path("/tmp") / f"{settings.FOLDER_PREFIX}-{i}-test"
            if is_test
            else Path(settings.UPLOAD_PATH) / f"{settings.FOLDER_PREFIX}-{i}"
            for i in range(settings.NUM_DISKS)
        ]
        self.__create_block()

    def __create_block(self):
        for path in self.block_path:
            logger.warning(f"Creating folder: {path}")
            path.mkdir(parents=True, exist_ok=True)

    #def remove_all(self, filename:str):
    #    for i in range(0, settings.NUM_DISKS):
    #        filepath=str(self.block_path[i])+"/"+filename
    #        if os.path.exists(filepath):
    #            os.remove(filepath)

    #@APP.exception_handler(RequestEntityTooLarge)
    #async def request_entity_too_large_exception_handler(request, exc) -> schemas.Msg:
    #    return schemas.Msg(
    #        detail="File Too Large",
    #    )


    async def file_integrity(self, filename: str) -> bool:
        """TODO: check if file integrity is valid
        file integrated must satisfy following conditions:
            1. all data blocks must exist
            2. size of all data blocks must be equal
            3. parity block must exist
            4. parity verify must success

        if one of the above conditions is not satisfied
        the file does not exist
        and the file is considered to be damaged
        so we need to delete the file
        """
        block_size=0
        xor_string=b""
        for i in range(0, settings.NUM_DISKS):
            filepath=str(self.block_path[i])+"/"+filename
            if os.path.exists(filepath):
                print(filepath + " exists!")
                if i==0:
                    block_size=os.path.getsize(filepath)
                    with open(filepath, "rb") as fp:
                        xor_string=fp.read()
                else:
                    if block_size != os.path.getsize(filepath):
                        # size inequal
                        remove_all(self, filename)
                        return False
                    with open(filepath, "rb") as fp:
                        temp=fp.read()
                        if i != settings.NUM_DISKS-1:
                            xor_string=bytes([a^b for a, b in zip(xor_string, temp)])
                        else:
                            if xor_string != temp:
                                # parity verify false!!
                                remove_all(self, filename)
                                return False
            else:
                #block missing
                remove_all(self, filename)
                return False
            
        return True
    
    #async def too_large_exception
    async def create_file(self, file: UploadFile) -> schemas.File:
        # TODO: create file with data block and parity block and return it's schema
        content = "お前はもう死んでいる!!!"
        #content = "123"
        #print("\n\n\n\n\n")
        #print(type(content_string)) 
        test_filename=file.filename
        #bbb=file_integrity(self, test_filename)
        #await bbb
        # print(test_filename)
        file.file.seek(0,2)
        file_size=file.file.tell()
        #if file_size > settings.MAX_SIZE:
        #    raise HTTPException(status_code=400, detail="File too large")
        await file.seek(0)
        if os.path.exists(str(self.block_path[0])+"/"+test_filename):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="File already exists")
        if file_size > settings.MAX_SIZE:
            #raise RequestEntityTooLarge()
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File too large")
            #return schemas.Msg(
            #    detail="File too large"
            #)
        content2 = file.file.read()
        #print(content2)
        #content_string = str(content2, encoding='utf-8')
        
        quo = int(file_size/(settings.NUM_DISKS-1))
        rem = file_size%(settings.NUM_DISKS-1)
        pos = 0
        #print(quo)
        xor_string=b""
        fix_dot=1
        if rem==0:
            fix_dot=0
        for i in range(0, settings.NUM_DISKS-1):
            #print(pos)
            #print(self.block_path[i])
            trim_string=b""
            if rem > 0:
                #await asyncio.sleep(1)
                trim_string=content2[pos:pos+quo+1]
                #print(rem)
                rem = rem - 1
                pos = pos+quo+1
            else:
                #await asyncio.sleep(1)
                trim_string=content2[pos:pos+quo]
                if fix_dot==1:
                    trim_string = trim_string + b'\x00'
                pos = pos+quo
            path=str(self.block_path[i])+"/"+test_filename
            #print(path)
            #print(trim_string)
            if i==0:
                xor_string=trim_string
            else:
                xor_string = bytes([a ^ b for a, b in zip(xor_string, trim_string)])
            with open(path, 'wb') as fp:
                fp.write(trim_string)
        path=str(self.block_path[settings.NUM_DISKS-1])+"/"+test_filename
        #print(xor_string)
        
        with open(path, 'wb') as fp:
            fp.write(xor_string)
        
        ''' 
        return schemas.File(
            name=test_filename,
            #name="meow.txt"
            size=file_size,
            checksum=hashlib.md5(content2).hexdigest(),
            content=base64.b64encode(content2),
            #content=content_string,
            content_type=file.content_type,
        )
        '''
        #print(base64.b64encode(content2).decode('UTF-8'))
        return schemas.File(
            name=test_filename,
            size=file_size,
            checksum=hashlib.md5(content2).hexdigest(),
            content=base64.b64encode(content2).decode('UTF-8'),
            content_type=file.content_type,
        )
        
        

    async def retrieve_file(self, filename: str) -> bytes:
        # TODO: retrieve the binary data of file
        #bbb=file_integrity(self, filename)
        returnfile=b""
        for i in range(0, settings.NUM_DISKS-1):
            filepath=str(self.block_path[i])+"/"+filename
            if os.path.exists(filepath):
                with open(filepath, "rb") as fp:
                    temp=fp.read()
                    if temp.endswith(b"\x00"):
                        temp = temp[:-1]
                    returnfile=returnfile+temp
            else:
                #for j in range(0, settings.NUM_DISKS):
                #    path_del = str(self.block_path[j])+"/"+filename
                #    if os.path.exists(path_del):
                #        os.remove(path_del)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found"
                )

        return returnfile
        #return b"".join("m3ow".encode() for _ in range(100))

    async def update_file(self, file: UploadFile) -> schemas.File:
        # TODO: update file's data block and parity block and return it's schema
        #bbb=file_integrity(self, filename)
        content = "何?!"
        filename=file.filename
        file.file.seek(0,2)
        file_size=file.file.tell()
        await file.seek(0)
        if os.path.exists(str(self.block_path[0])+"/"+filename):
            content="123456"
        #else:
        #    raise HTTPException(
        #            status_code=status.HTTP_404_NOT_FOUND,
        #            detail="File not found"
        #    )
            if file_size > settings.MAX_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="File too large"
                )
            else:
                #return schemas.File(
                #    name="m3ow.txt",
                #    size=123,
                #    checksum=hashlib.md5(content.encode()).hexdigest(),
                #    content=base64.b64decode(content.encode()),
                #    content_type="text/plain",
                #)
                content2 = file.file.read()
                quo = int(file_size/(settings.NUM_DISKS-1))
                rem = file_size%(settings.NUM_DISKS-1)
                pos = 0
                xor_string=b""
                fix_dot=1
                if rem == 0:
                    fix_dot=0
                for i in range(0, settings.NUM_DISKS-1):
                    trim_string=b""
                    if rem>0:
                        trim_string=content2[pos:pos+quo+1]
                        rem = rem-1
                        pos = pos+quo+1
                    else:
                        trim_string=content2[pos:pos+quo]
                        if fix_dot==1:
                            trim_string = trim_string+b'\x00'
                        pos = pos+quo
                    path=str(self.block_path[i])+"/"+filename
                    if i == 0:
                        xor_string=trim_string
                    else:
                        xor_string = bytes([a^b for a, b in zip(xor_string, trim_string)])
                    with open(path, 'wb') as fp:
                        fp.write(trim_string)
                path=str(self.block_path[settings.NUM_DISKS-1])+"/"+filename
                with open(path, 'wb') as fp:
                    fp.write(xor_string)
                return schemas.File(
                    name=filename,
                    size=file_size,
                    checksum=hashlib.md5(content2).hexdigest(),
                    content=base64.b64encode(content2).decode('UTF-8'),
                    content_type=file.content_type,
                )
        else:
            #for j in range(0, settings.NUM_DISKS):
            #    path_del=str(self.block_path[j])+"/"+filename
            #    if os.path.exists(path_del):
            #        os.remove(path_del)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )

    async def delete_file(self, filename: str) -> None:
        # TODO: delete file's data block and parity block
        #bbb=file_integrity(self, filename)
        if os.path.exists(str(self.block_path[0])+"/"+filename):
            pppp=1
        else:
            #for j in range(0, settings.NUM_DISKS):
            #    path_del=str(self.block_path[j])+"/"+filename
            #    if os.path.exists(path_del):
            #        os.remove(path_del)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        for i in range(0, settings.NUM_DISKS):
            path_del=str(self.block_path[i])+"/"+filename
            if os.path.exists(path_del):
                os.remove(str(self.block_path[i])+"/"+filename) 
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail="File deleted"
        )
        #except ValidationError as e:
        #    print(e)
        pass

    '''
    async def fix_block(self, block_id: int) -> None:
        # TODO: fix the broke block by using rest of block
        pass
    '''
    async def fix_block(self, block_id: int) -> None:
        # TODO: fix the broke block by using rest of block
        fix_string = ""
        temp_num=block_id-1
        if temp_num<0:
            temp_num=block_id+1
        parity_block_path = str(self.block_path[temp_num])
        parity_dir_list = os.listdir(parity_block_path)
        file_name = parity_dir_list[0]
        #parity_path = str(self.block_path[settings.NUM_DISKS - 1]) + "/" + file_name
        #with open(parity_path, 'rb') as fp:
        #    fix_string = fp.read()
        for i in range(0, settings.NUM_DISKS):
            if i != block_id:
                data_path = str(self.block_path[i]) + "/" + file_name
                if os.path.exists(data_path):
                    with open(data_path, 'rb') as fp:
                        if fix_string=="":
                            fix_string=fp.read()
                        else:
                            tmp_string = fp.read()
                            fix_string = bytes([a ^ b for a, b in zip(tmp_string, fix_string)])
        fix_path = str(self.block_path[block_id]) + "/" + file_name
        self.block_path[block_id].mkdir(parents=True, exist_ok=True)
        with open(fix_path, 'wb') as fp:
            fp.write(fix_string)
        pass


storage: Storage = Storage(is_test="pytest" in sys.modules)
