/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie.tools;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.DatagramPacket;
import java.net.Inet6Address;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.MulticastSocket;
import java.net.NetworkInterface;
import java.net.Socket;
import java.net.SocketException;
import java.util.ArrayList;
import java.util.Enumeration;
import java.util.logging.Level;
import java.util.logging.Logger;

//import valerie.tools.DebugOutput;

/**
 *
 * @author Admin
 */
public class Network {

    int MAX_CHARS_TCP = 1460;

    public String sendBroadcast()
    {
        DebugOutput.printl("->");

        String rtv = "";

        byte[] RecieveBuf = new byte [256];
        byte[] SendBuf =  new byte [256];
        String servReq = "SERV_REQ";
        byte[] bServReq = servReq.getBytes();
        NetworkInterface ntAdapter = null;
        Enumeration enu;
        try {
            enu = NetworkInterface.getNetworkInterfaces();
        } catch (SocketException ex) {
            Logger.getLogger(Network.class.getName()).log(Level.SEVERE, null, ex);
            return rtv;
        }
        while(enu.hasMoreElements())
        {
           ntAdapter = (NetworkInterface)enu.nextElement();
           Enumeration e = ntAdapter.getInetAddresses();

           while(e.hasMoreElements())
           {
                InetAddress myAddr = (InetAddress)e.nextElement();
                //DebugOutput.printl(myAddr.getClass().toString());
                if (myAddr instanceof Inet6Address)
                    continue; //We dont support ipv6
                DebugOutput.printl("Adapter Display Name :"+ntAdapter.getDisplayName());
                DebugOutput.printl("Adapter Name : "+ntAdapter.getName());
                DebugOutput.printl("Ip : "+myAddr.getHostAddress());

                byte[] bMyAddr = myAddr.getHostAddress().getBytes();

                int iter = 0;
                for(byte b : bServReq)
                    SendBuf[iter++] = b;

                for(byte b : bMyAddr)
                    SendBuf[iter++] = b;

                MulticastSocket socket;
                try {
                    Integer Port = 5450;
                    socket = new MulticastSocket(new InetSocketAddress(myAddr.getHostAddress(), Port));
                    socket.setBroadcast(true);
                    InetAddress Adr = InetAddress.getByName("255.255.255.255");
                    Integer WaitMilliSeconds = 50;
                    DatagramPacket Send = new DatagramPacket(SendBuf, SendBuf.length, Adr, Port);
                    socket.setSoTimeout(WaitMilliSeconds);
                    socket.send(Send);

                    //DatagramPacket Recieve = new DatagramPacket (RecieveBuf, RecieveBuf.length);
                    do
                    {//warten auf Antworten
                        DatagramPacket Recieve = new DatagramPacket (RecieveBuf, RecieveBuf.length);
                        socket.receive(Recieve);

                        String boxinfo = new String(Recieve.getData()).trim();
                        if(!boxinfo.startsWith("SERV_REQ")) { // This would be echo
                            boxinfo += "IPADDR=" + Recieve.getAddress().getHostAddress() + ";|";

                            DebugOutput.printl(boxinfo.trim());

                            rtv += boxinfo;
                        }
                        //We only want the Boxinfo an the BoxIP for now.
                        //break;
                    } while(!socket.isClosed());
                    socket.close();
                } catch(Exception ex) {
                    DebugOutput.printl(ex.toString());
                }
           }
        }

        DebugOutput.printl("<-");

        return rtv;
    }

     public boolean sendSmartFile(InetAddress addr, String fileOnPc, String  directoryOnBox) {
        //DebugOutput.printl("->");

        boolean rtv = false;
        boolean result = new File(fileOnPc).isFile();
        if(result)
            rtv = sendFile(addr, fileOnPc, directoryOnBox);
        else {
            DebugOutput.printl("File not found ("+fileOnPc+")");
            rtv = false;
        }
        //DebugOutput.printl("<-");
        return rtv;
    }

    public boolean sendFile(InetAddress addr, String file, String  directory) {
        boolean rtv = false;
        DebugOutput.printl("->");
        try {
            Socket clientSocket = new Socket(addr, 5451);

            OutputStream dataOutput = clientSocket.getOutputStream();
            File inputFile = new File(file);
            FileInputStream in = new FileInputStream(inputFile);

            byte[] buffer = new byte[MAX_CHARS_TCP];
            int numread;

            String sPrefix = "REQ_FILE_MT";
            byte[] bPrefix = sPrefix.getBytes();
            dataOutput.write(bPrefix, 0, bPrefix.length);

            {
                String sName = directory + "/" + inputFile.getName();
                byte[] bName = sName.getBytes();

                Integer iLength = bName.length;
                Integer iByte0 = iLength  >> 8;
                Integer iByte1 = iLength & 0xFF;
                byte[] bLength = new byte[2];
                bLength[0] = (byte)(iByte1%0x100);
                bLength[1] = (byte)(iByte0%0x100);
                dataOutput.write(bLength, 0, bLength.length);
                dataOutput.write(bName, 0, bName.length);
            }
            
            {
                Integer iLength = (int)new File(file).length();
                Integer iByte3 = (iLength  >> 24)& 0xFF;
                Integer iByte2 = (iLength  >> 16)& 0xFF;
                Integer iByte1 = (iLength  >> 8)& 0xFF;
                Integer iByte0 = iLength & 0xFF;
                byte[] bLength = new byte[4];
                bLength[0] = (byte)(iByte0%0x100);
                bLength[1] = (byte)(iByte1%0x100);
                bLength[2] = (byte)(iByte2%0x100);
                bLength[3] = (byte)(iByte3%0x100);
                dataOutput.write(bLength, 0, bLength.length);

                DebugOutput.print("Sending: "+directory+"/"+file); // console confirmation of transfer
                while ((numread = in.read(buffer))>=0) {
                    dataOutput.write(buffer, 0, numread);
                    System.out.print("."); // console confirmation of transfer
                }
                System.out.println("");
            }

            in.close();
            dataOutput.close();
            clientSocket.close();
            rtv = true;
        } catch(Exception ex) {
            DebugOutput.printl("Could not send file ("+file+") to box ("+addr.getHostAddress()+")");
            DebugOutput.printl(ex.toString());
            //DebugOutput.printl("");
            rtv = false;
        }

        DebugOutput.printl("<-");
        return rtv;
    }

    public boolean getSmartFile(InetAddress addr, String fileOnBox, String directoryOnPC) {
        DebugOutput.printl("->");

        boolean rtv = false;
        String[] result = sendCMD(addr, "ls " + fileOnBox);
        if(result != null && result.length > 0 && result[0].equals(fileOnBox))
            rtv = getFile(addr, fileOnBox, directoryOnPC);
        else {
            DebugOutput.printl("File not found ("+fileOnBox+")");
            rtv = false;
        }
        DebugOutput.printl("<-");
        return rtv;
    }

    public boolean getFile(InetAddress addr, String fileOnBox, String directoryOnPC) {
        DebugOutput.printl("->");
        try {
            Socket clientSocket = new Socket(addr, 5451);

            OutputStream dataOutput = clientSocket.getOutputStream();
            InputStream dataInput = clientSocket.getInputStream();

            File fileOnPC = new File(directoryOnPC + "/" + new File(fileOnBox).getName());
            FileOutputStream fileOnPCOutStream = new FileOutputStream(fileOnPC);


            byte[] buffer = new byte[MAX_CHARS_TCP];
            int numread;

            { // SEND REQUEST STRING
                String sPrefix = "REQ_FILE_MO";
                byte[] bPrefix = sPrefix.getBytes();
                dataOutput.write(bPrefix, 0, bPrefix.length);
            }

            { // SEND FILENAME
                String sName = fileOnBox;
                byte[] bName = sName.getBytes();

                Integer iLength = bName.length;
                Integer iByte0 = iLength  >> 8;
                Integer iByte1 = iLength & 0xFF;
                byte[] bLength = new byte[2];
                bLength[0] = (byte)(iByte1%0x100);
                bLength[1] = (byte)(iByte0%0x100);
                dataOutput.write(bLength, 0, bLength.length);
                dataOutput.write(bName, 0, bName.length);
            }

            Integer iLength = 0;
            { // GET SIZE OF REQUESTED FILE
                byte[] bLength = new byte[4];
                if (dataInput.read(bLength, 0, 4) != 4)
                    return false;

                iLength = 0;
                iLength |= (int)((int) bLength[3] & 0xFF);
                iLength <<= 8;
                iLength |= (int)((int) bLength[2] & 0xFF);
                iLength <<= 8;
                iLength |= (int)((int) bLength[1] & 0xFF);
                iLength <<= 8;
                iLength |= (int)((int) bLength[0] & 0xFF);
                if (iLength <= 0)
                    return false;
            }

            {
                int i = 0;
                for (i = 0; i < iLength; ) {
                    int bytesToRead = (iLength - i)>MAX_CHARS_TCP?MAX_CHARS_TCP:iLength-i;
                    numread = dataInput.read(buffer, 0, bytesToRead);
                    fileOnPCOutStream.write(buffer, 0, numread);
                    i += numread;
                    System.out.print("."); // console confirmation of transfer
                }
            }

            fileOnPCOutStream.close();
            dataInput.close();
            dataOutput.close();
            clientSocket.close();
        } catch(Exception ex) {
            DebugOutput.printl("Could not get file ("+fileOnBox+") from box ("+addr.getHostAddress()+")");
            DebugOutput.printl(ex.toString());
            //DebugOutput.printl("");
        }

        DebugOutput.printl("<-");
        return true;
    }

    String rtvBuffer = "";

    public String[] sendCMD(InetAddress addr, String cmd) {
        DebugOutput.printl("-> " + cmd);

        //As we dont get stderr, lets 'disable' it here
        cmd = cmd + " 2> /dev/null";

        ArrayList<String> list = new ArrayList<String>();
        try {
            Socket clientSocket = new Socket(addr, 5451);

            boolean connected  = clientSocket.isConnected();
            if(!connected)
                clientSocket.connect(new InetSocketAddress(addr, 5451), 1000);

            OutputStream dataOutput = clientSocket.getOutputStream();
            InputStream dataInput = clientSocket.getInputStream();

            String sPrefix = "REQ_CMDEXEC";
            byte[] bPrefix = sPrefix.getBytes();
            dataOutput.write(bPrefix, 0, bPrefix.length);

            byte[] bName = cmd.getBytes();
            byte[] bMsgId = new byte[1];
            //Integer iMsgId = 0;
            Integer iLength = bName.length;
            Integer iByte0 = (iLength % 0x100) >> 8;
            Integer iByte1 = iLength & 0xFF;
            byte[] bLength = new byte[2];
            bLength[0] = (byte)(iByte1%0xFF);
            bLength[1] = (byte)(iByte0%0xFF);
            dataOutput.write(bLength, 0, bLength.length);
            dataOutput.write(bName, 0, bName.length);
            
            InputStreamReader converter = new InputStreamReader(dataInput);
            BufferedReader reader=new BufferedReader(converter);
            String line;
            while((line=reader.readLine())!=null){
            	list.add(line.substring(2));
            	DebugOutput.print(String.format("[%03d] %s\n", line.length(),line.substring(2)));
            }

            dataOutput.close();
            clientSocket.close();
        } catch(Exception ex) {
            DebugOutput.printl("Could not exec cmd ("+cmd+") from box ("+addr.getHostAddress()+")");
            DebugOutput.printl(ex.toString());
        }

        DebugOutput.printl("<-");

        return (String []) list.toArray (new String [list.size ()]);
    }
}
