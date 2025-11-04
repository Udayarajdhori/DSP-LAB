sequenceDiagram
    participant ClientA
    participant Server
    participant ClientB

    ClientA->>Server: TCP Handshake (TLS)
    Server-->>ClientA: Secure Connection Established

    ClientB->>Server: TCP Handshake (TLS)
    Server-->>ClientB: Secure Connection Established

    Note over ClientA, ClientB: Both clients establish a shared secret key for E2EE (pre-shared in this demo)

    ClientA->>ClientA: Encrypts message with shared key
    ClientA->>Server: Sends encrypted message
    
    Server->>ClientB: Relays encrypted message
    
    ClientB->>ClientB: Decrypts message with shared key
