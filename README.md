# OSNT
Course Project 

Title : DTLS in NeST

1. Short Notes on TLS
2. DTLS and TLS difference and their respective features
3. Implementation of DTLS using linux namespaces
4. Understanding NeST and Installation


## Datagram Transport Layer Security (DTLS)

<details>
<summary>Overview</summary>

Datagram Transport Layer Security (DTLS) is a protocol that provides the strong security guarantees of Transport Layer Security (TLS) to **datagram-based protocols** like UDP. Applications such as **media streaming, online gaming, and Internet telephony** often use UDP for its low-latency, delay-sensitive nature. DTLS secures these applications without changing their fundamental behavior.  

DTLS is designed to be **as similar to TLS as possible**, maximizing code reuse and minimizing new security complexities.  
</details>

<details>
<summary>Why TLS Cannot Run Directly on UDP</summary>

TLS was designed for reliable, connection-oriented transports like TCP. UDP is **unreliable**, which introduces two major issues:

<details>
<summary>1. Packet Loss and Reordering</summary>
- TLS assumes messages are delivered reliably and in order.  
- Loss of a record causes the MAC (Message Authentication Code) check of subsequent records to fail.  
- The TLS handshake is "lockstep," breaking if messages are lost or reordered.  
</details>

<details>
<summary>2. Lack of Independent Record Decryption</summary>
- In some TLS modes (e.g., stream ciphers), the cryptographic context depends on previous records.  
- Loss of a record prevents decryption of subsequent messages.  
</details>

</details>

<details>
<summary>How DTLS Adapts TLS for UDP</summary>

DTLS modifies TLS minimally but crucially to support unreliable datagram transport.

<details>
<summary>Mechanisms for Unreliable Transport</summary>
  
 **Explicit Sequence Numbers**:
     Each DTLS record includes an **epoch** and **sequence number** to allow proper MAC verification even if packets arrive out of order.  

 **Reliable Handshake**:  
  - **Retransmission Timers**: Each flight of handshake messages is retransmitted if a response is not received. Initial timer = 1s, doubles on each retransmission.  
  - **Handshake Message Sequence Numbers (`message_seq`)**: Messages are numbered to handle reordering.  
  - **Fragmentation**: Large handshake messages are fragmented across multiple DTLS records with offset and length information for reassembly.  
</details>

<details>
<summary>Security Mechanisms</summary>
DTLS provides privacy, integrity, and protection against message forgery, with security guarantees equivalent to TLS.

- **Denial-of-Service (DoS) Countermeasures**  
  - **Stateless Cookie Exchange**: Prevents amplification attacks using spoofed IP addresses.  
    1. Client sends initial `ClientHello`.  
    2. Server responds with `HelloVerifyRequest` containing a stateless cookie.  
    3. Client resends `ClientHello` including the cookie.  
    4. Server verifies the cookie before allocating resources.  

- **Record Payload Protection**  
  - **Anti-Replay**: Uses a sliding window to detect duplicate or old records.  
  - **MAC for Integrity**: MAC calculation includes the epoch and sequence number. Invalid records are discarded without terminating the connection.  
  - **Banning Incompatible Ciphers**: Stream ciphers like RC4 are prohibited as they cannot handle record loss.  
</details>

</details>

<details>
<summary>DTLS Handshake Process over UDP</summary>

DTLS modifies the TLS handshake to accommodate UDP's unreliability and add DoS protection. Messages are grouped into **flights** for retransmission.

<details>
<summary>Handshake Flights</summary>

1. **Flight 1 (Client → Server)**  
   - Client sends `ClientHello` (empty cookie).  
   - Starts retransmission timer.  

2. **Flight 2 (Server → Client)**  
   - Server sends `HelloVerifyRequest` with a stateless cookie.  
   - No state is allocated yet.  

3. **Flight 3 (Client → Server)**  
   - Client resends `ClientHello` with cookie.  
   - Starts retransmission timer.  

4. **Flight 4 (Server → Client)**  
   - Server validates cookie and sends `ServerHello`, `Certificate`, `ServerKeyExchange` (if needed), and `ServerHelloDone`.  
   - Starts retransmission timer.  

5. **Flight 5 (Client → Server)**  
   - Client responds with `Certificate` (if requested), `ClientKeyExchange`, `CertificateVerify` (if needed), `ChangeCipherSpec`, and encrypted `Finished`.  

6. **Flight 6 (Server → Client)**  
   - Server verifies `Finished` and sends its own `ChangeCipherSpec` and encrypted `Finished`.  

> Once both sides exchange `Finished` messages, the handshake is complete. Encrypted application data can now be exchanged while maintaining UDP semantics (no retransmission or reordering by DTLS).  
</details>

</details>
