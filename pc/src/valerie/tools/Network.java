/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie.tools;

import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.DatagramPacket;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.MulticastSocket;
import java.net.Socket;
import java.util.ArrayList;

/**
 *
 * @author Admin
 */
public class Network {

    public String sendBroadcast()
    {
        String rtv = "";

        byte[] RecieveBuf = new byte [256];
        byte[] SendBuf =  new byte [256];

        InetAddress myAddr = null;
        try {
               myAddr = InetAddress.getLocalHost();
        }catch(Exception ex) {}

        String servReq = "SERV_REQ";
        byte[] bServReq = servReq.getBytes();
        byte[] bMyAddr = myAddr.getHostAddress().getBytes();

        int iter = 0;
        for(byte b : bServReq)
            SendBuf[iter++] = b;

        for(byte b : bMyAddr)
            SendBuf[iter++] = b;
        
        MulticastSocket socket;
        try {
            socket = new MulticastSocket();
            socket.setBroadcast(true);
            InetAddress Adr = InetAddress.getByName("255.255.255.255");
            Integer Port = 5450;
            Integer WaitMilliSeconds = 1000;
            DatagramPacket Send = new DatagramPacket(SendBuf, SendBuf.length, Adr, Port);
            socket.setSoTimeout(WaitMilliSeconds);
            socket.send(Send);

            DatagramPacket Recieve = new DatagramPacket (RecieveBuf, RecieveBuf.length);
            //do
            {//warten auf Antworten
                socket.receive(Recieve);
                rtv = new String(Recieve.getData());

                rtv = rtv.trim();

                rtv += "IPADDR=" + Recieve.getAddress().toString().substring(1) + ";";

                System.out.println(rtv);

                //We only want the Boxinfo an the BoxIP for now.
                //break;
            }// while(!socket.isClosed());
            socket.close();
        } catch(Exception ex) {
            System.out.println(ex.toString());
        }

         System.out.println("Success");

         return rtv;
    }

    public void sendFile(InetAddress addr, String file, String  directory) {

        try {
            Socket clientSocket = new Socket(addr, 5451);

            OutputStream dataOutput = clientSocket.getOutputStream();
            File inputFile = new File(file);
            FileInputStream in = new FileInputStream(inputFile);

            byte[] buffer = new byte[2048];
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

                while ((numread = in.read(buffer))>=0) {
                    dataOutput.write(buffer, 0, numread);
                    System.out.println("sending..." + numread); // console confirmation of transfer
                }
            }

            in.close();
            dataOutput.close();
            clientSocket.close();
        } catch(Exception ex) {
            System.out.println(ex.toString());
        }
    }

    String rtvBuffer = "";

    public String[] sendCMD(InetAddress addr, String cmd) {

        ArrayList list = new ArrayList();
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

            Integer iLength = bName.length;
            Integer iByte0 = (iLength % 0x100) >> 8;
            Integer iByte1 = iLength & 0xFF;
            byte[] bLength = new byte[2];
            bLength[0] = (byte)(iByte0%0xFF);
            bLength[1] = (byte)(iByte1%0xFF);
            dataOutput.write(bLength, 0, bLength.length);
            dataOutput.write(bName, 0, bName.length);

            
            while(dataInput.read(bLength, 0, 2) > 0) {
                iByte0 =  bLength[0] & 0xFF;
                iByte1 =  bLength[1] & 0xFF;
                iByte1 = iByte1 << 8;
                iLength = iByte0;
                iLength += iByte1;
                byte[] bData = new byte[iLength];
                dataInput.read(bData, 0, iLength);
                
                String sData = new String(bData);
                sData = sData.substring(0, iLength-1);
                    System.out.printf("[%03d] %s\n", iLength, sData);
                    list.add(sData);
            }

            dataOutput.close();
            clientSocket.close();
        } catch(Exception ex) {
            System.out.println(ex.toString());
        }

        return (String []) list.toArray (new String [list.size ()]);
    }
}
