import rhona

if __name__=='__main__':
    srv = rhona.Server ()
    print ('Listening on port: {}'.format (srv.GetListenPort ()))
    srv.Run ()
