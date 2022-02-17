/*
 *
 *  UDPClient
 *  * Compile: java UDPClient.java
 *  * Run: java UDPClient
 */
import java.io.*;
import java.net.*;
import java.util.*;
import java.net.SocketException;


public class PingClient {
    private static final int TIMEOUT = 600;

	public static void main(String[] args) throws Exception {
		// Define socket parameters, address and Port No
		// change above port number if required
        if (args.length != 2) {
            System.out.println("Required arguments: host port");
            return;
        }
        InetAddress IPAddress = InetAddress.getByName(args[0]);   
		int serverPort = Integer.parseInt(args[1]);

		// create socket which connects to server
		DatagramSocket clientSocket = new DatagramSocket();
        clientSocket.setSoTimeout(TIMEOUT);

        int seq = 3331;
        long total_rtt = 0;
        long max_rtt = 0;
        long min_rtt = 600;
        while (seq < 3346) {
            long rtt = 0;
            String message = "ping to " + args[0] + ", ";
            try {
                //prepare for sending
                byte[] sendData = new byte[1024];
                sendData = message.getBytes();

                // write to server, need to create DatagramPAcket with server address and port No
                DatagramPacket sendPacket = new DatagramPacket(sendData,sendData.length,IPAddress,serverPort);

                //actual send call
                clientSocket.send(sendPacket);
                long starttime = System.nanoTime();

                //prepare buffer to receive reply
                byte[] receiveData=new byte[1024];

                // receive from server
                DatagramPacket receivePacket = new DatagramPacket(receiveData,receiveData.length);
                clientSocket.receive(receivePacket);
                long endtime = System.nanoTime();
                
                rtt = (endtime - starttime)/(1000000);
                total_rtt += rtt;

                if (rtt >= max_rtt) {
                    max_rtt = rtt;
                }
                if (rtt <= min_rtt) {
                    min_rtt = rtt;
                }
                System.out.println("ping to " + args[0] + ", " + "seq = " + seq + ", rtt = " + rtt + " ms\r\n");
                
            } catch (SocketTimeoutException e) {
                System.out.println("ping to " + args[0] + ", " + "seq = " + seq + ", rtt = " + "timeout\r\n");
            }
            seq = seq + 1;
        }

        clientSocket.close();
        System.out.println("min = " + min_rtt + " ms, " + "max = " + max_rtt + " ms, avg = " + (total_rtt/15) + " ms\r\n");
        //close the socket
	} // end of main
} // end of class