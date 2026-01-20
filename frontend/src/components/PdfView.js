import { Button } from "react-bootstrap";
import axios from 'axios';
import { useEffect, useState } from "react";


const base64ToBlobUrl = (base64) => {
  const byteCharacters = atob(base64);
  const byteNumbers = new Array(byteCharacters.length);

  for (let i = 0; i < byteCharacters.length; i++) {
    byteNumbers[i] = byteCharacters.charCodeAt(i);
  }

  const byteArray = new Uint8Array(byteNumbers);
  const blob = new Blob([byteArray], { type: "application/pdf" });
  return URL.createObjectURL(blob);
}

const PdfView = (props) => {
    const [src, setSrc] = useState(null);

    useEffect(() => {
        setSrc(null);
        getS3Document();
    }, [props.idToken, props.s3Path]);

    const getS3Document = () => {
        if (!props.idToken || !props.s3Path) return;
        axios.get(`${process.env.REACT_APP_GATEWAY_URL}/s3?s3_path=${props.s3Path}`, {
            headers: {
                'Authorization': `Bearer ${props.idToken}`,
                'Content-Type': 'application/json',
            },
        })
        .then(response => {
            const url = base64ToBlobUrl(response.data);
            setSrc(url);
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
    }

    useEffect(() => {
    }, [props.idToken, props.s3Path]);

    return (
        <>
            {src &&
                <iframe
                    src={src}
                    style={{ width: "100%", height: "100%", border: "none" }}
                    title="PDF"
                />
            }
        </>
    )
}

export default PdfView;
