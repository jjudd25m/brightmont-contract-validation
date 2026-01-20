// import { useState, useEffect } from "react";
import { Amplify } from "aws-amplify";
import { withAuthenticator } from "@aws-amplify/ui-react";
import "@aws-amplify/ui-react/styles.css";
import { fetchAuthSession } from "aws-amplify/auth";
import 'bootstrap/dist/css/bootstrap.min.css';
import { Button } from "react-bootstrap";
import { useEffect, useState } from "react";
import axios from 'axios';
import AgreementForm from "./components/AgreementForm";
import PdfView from "./components/PdfView";

import {
    PanelGroup,
    Panel,
    PanelResizeHandle
} from "react-resizable-panels";

import "./app.css";


Amplify.configure({
    Auth: {
        Cognito: {
            userPoolId: "us-east-1_8bHCf97l4",
            userPoolClientId: "6ubh3imdc1o33im3kd18j7omkg"
        }
    }
});


async function loadIdToken() {
    try {
        const session = await fetchAuthSession();
        const token = session.tokens.idToken.toString();
        return token;
    } catch (err) {
        console.error("Failed to fetch the token", err);
    }
}


function App({ signOut, user }) {
    const [s3Paths, setS3Paths] = useState([]);
    const [s3Path, setS3Path] = useState(null);
    const [idToken, setIdToken] = useState("");

    const setNewS3Path = (path) => {
        if (s3Path === path) { return; }
        setS3Path(path);
    }

    // search
    const [search, setSearch] = useState("");
    const filteredPaths = s3Paths.filter(path =>
        path.toLowerCase().includes(search.toLowerCase())
    ).sort((a, b) =>
        a.localeCompare(b, undefined, { sensitivity: "base" })
    );;

    useEffect(() => {
        if (!idToken) return;
        axios.get(`${process.env.REACT_APP_GATEWAY_URL}/agreements`, {
            headers: {
                'Authorization': `Bearer ${idToken}`,
                'Content-Type': 'application/json',
            },
        })
        .then(response => {
            setS3Paths(response.data);
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
    }, [idToken]);

    useEffect(() => {
        loadIdToken().then((idToken) => {
            setIdToken(idToken);
        });
    }, []);

    return (
        <PanelGroup direction="horizontal" style={{ height: "100vh" }}>
          <Panel defaultSize={60} minSize={30}>
              <PdfView s3Path={s3Path} idToken={idToken} />
          </Panel>

          <PanelResizeHandle style={{ width: "6px", cursor: "col-resize", background: "#ddd" }} />
            <Panel defaultSize={40} minSize={20} style={{ marginLeft: "10px"}}>
                <h1 style={{ textAlign:"center" }}>
                    test cicd 2
                    Welcome {user.username}!
                    <Button onClick={signOut}>Logout</Button>
                </h1>
                <input
                    type="text"
                    placeholder="Search files..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    style={{
                        width: "100%",
                        marginBottom: "10px",
                        padding: "6px",
                        borderRadius: "4px",
                    }}
                />
                <div style={{ maxHeight: "100px", overflowY: "auto",
                    scrollbarGutter: "stable both-edges", paddingRight: "8px",
                    border: "1px solid #ccc" }}>

                    {filteredPaths.map((path, index) => (
                        <div
                            key={index}
                            role="button"
                            style={{
                                backgroundColor: path === s3Path ? "#007bff" : "transparent",
                                color: path === s3Path ? "#fff" : "inherit",
                                cursor: "pointer",
                            }}
                            onClick={() => setNewS3Path(path)}
                        >
                            •{path}
                        </div>
                    ))}

                    {filteredPaths.length === 0 && (
                      <div style={{ padding: "8px", color: "#777" }}>
                        No matches found ❌
                      </div>
                    )}
                </div>

                <hr/>

                <AgreementForm s3Path={s3Path} idToken={idToken} />
            </Panel>
        </PanelGroup>
    );
}

export default withAuthenticator(App, {
    hideSignUp: true
});
