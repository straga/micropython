import logging
log = logging.getLogger("PLATFORM")
log.setLevel(logging.INFO)


#upy
async def upy_awrite(writer, data):

    try:
        await writer.awrite(data)
    except Exception as e:
        log.debug("Error: write: {}".format(e))
        pass


async def upy_aclose(writer):
    try:
        await writer.aclose()
    except Exception as e:
        log.debug("close: {}".format(e))
        pass


def _try_alloc_byte_array(size):
    import gc
    for x in range(10):
        try:
            gc.collect()
            return bytearray(size)
        except:
            log.debug("Error alloc byte ")
            pass

    return None


def upy_buffer(default=64):
    return _try_alloc_byte_array(default)


async def upy_buffer_writer(awrite, writer, buf, x):

    try:
        await writer.awrite(buf, 0, x)
    except Exception as err:
        log.error("BUF:{}".format(err))
        pass





