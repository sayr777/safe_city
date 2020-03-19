import grpc
import API_pb2
import API_pb2_grpc
import datetime


# ------------------------------------------------------
# get the latest telematics messages for the BNSO list
# gRPC_URL - address and port of the RNIS grpc server
# DEVICES - BNSO list
# ------------------------------------------------------
def get_grpc_states_from_devices(gRPC_URL, DEVICES):
    # to declare a list of telematics
    telematic_message_list = []
    # open a gRPC channel
    try:
        channel = grpc.insecure_channel(gRPC_URL)
    except:
        print('Channel opening error')
        return []
    # close a gRPC channel
    channel.close
    # create a stub (client)
    client = API_pb2_grpc.APIStub(channel)
    # create a valid request message
    request = API_pb2.ObjectsStateRequest \
        (Filter=API_pb2.DataFilter(DeviceCode=DEVICES), \
         Fields=API_pb2.FieldsToggle(Position=True, Ignition=True, Motohours=True, \
                                     Mileage=True, Moving=True, Ports=True, Address=True))
    # make the call
    try:
        result = client.GetObjectsState(request)
    except:
        print('Error getting data')
        return []

    # print result
    for point in result.Objects:
        # device_time = datetime.datetime.fromtimestamp(point.Data[0].DeviceTime).strftime('%Y-%m-%d %H:%M:%S'
        telematic_message_list.append( \
            [point.DeviceCode, \
             # device_time.strftime('%Y-%m-%d %H:%M:%S'),\
             point.Data[0].DeviceTime, \
             point.StateNumber, \
             point.Data[0].Position.Longitude, \
             point.Data[0].Position.Latitude, \
             point.Data[0].Position.Course, \
             point.Data[0].Position.Speed \
             ])
    return telematic_message_list



# ------------------------------------------------------
# get the latest telematics messages for the state number list
# gRPC_URL - address and port of the RNIS grpc server
# NUMBERS - state numbers list
# ------------------------------------------------------
def get_grpc_states_from_state_numbers(gRPC_URL, NUMBERS):
    # to declare a list of telematics
    telematic_message_list = []
    # open a gRPC channel
    try:
        channel = grpc.insecure_channel(gRPC_URL)
    except:
        print('Channel opening error')
        return []
    # close a gRPC channel
    channel.close
    # create a stub (client)
    client = API_pb2_grpc.APIStub(channel)
    # create a valid request message
    request = API_pb2.ObjectsStateRequest \
        (Filter=API_pb2.DataFilter(StateNumber=NUMBERS), \
         Fields=API_pb2.FieldsToggle(Position=True, Ignition=True, Motohours=True, \
                                     Mileage=True, Moving=True, Ports=True, Address=True))
    # make the call
    try:
        result = client.GetObjectsState(request)
    except:
        print('Error getting data')
        return []

    # print result
    for point in result.Objects:
        # device_time = datetime.datetime.fromtimestamp(point.Data[0].DeviceTime)
        telematic_message_list.append( \
            [point.DeviceCode, \
             # device_time.strftime('%Y-%m-%d %H:%M:%S'),\
             point.Data[0].DeviceTime, \
             point.StateNumber, \
             point.Data[0].Position.Longitude, \
             point.Data[0].Position.Latitude, \
             point.Data[0].Position.Course, \
             point.Data[0].Position.Speed \
             ])
    return telematic_message_list
