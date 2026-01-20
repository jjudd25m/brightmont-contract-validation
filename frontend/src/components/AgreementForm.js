import { Button } from "react-bootstrap";
import axios from 'axios';
import { useEffect, useState } from "react";
import OverlayTrigger from 'react-bootstrap/OverlayTrigger';
import Tooltip from 'react-bootstrap/Tooltip';

const EMPTY_AGREEMENT = {
    id: "",
    document_title: "",
    student_first_name: "",
    student_last_name: "",
    student_nickname: null,
    parent_guardian_full_name: "",
    parent_guardian_email: "",
    second_parent_guardian_full_name: "",
    second_parent_guardian_email: "",
    student_campus: "",
    student_courses: "",
    student_college_bound: "",
    automatic_renewal_authorization: null,
    scheduled_start_date: "",
    one_to_one_sessions: "",
    homework_studio_sessions: "",
    total_sessions_purchased: null,
    document_id: "",
    campus: null,
    college_bound: null,
    current_grade: "",
    total_tuition: "",
    s3_path: "",
    scholarship_type: null,
    scholarship_payment: null,
    is_single_payment: false,
    payment_amount: "",
    is_human_approved: true,
    services: Array.from({ length: 4 }, () => ({
        service_name: "",
        cost_per_unit: "",
        units: "",
        tuition: "",
    })),
};

const AgreementForm = (props) => {
    const [agreementData, setAgreementData] = useState(null);

    useEffect(() => {
        setAgreementData(EMPTY_AGREEMENT);
        getAgreementData();
    }, [props.idToken, props.s3Path]);

    const EMPTY_SERVICE = {
      service_name: "",
      cost_per_unit: "",
      units: "",
      tuition: ""
    };

    const normalizeServices = (services = []) => {
        const normalized = services.map(s => ({
            service_name: s.service_name ?? "",
            cost_per_unit: s.cost_per_unit ?? "",
            units: s.units ?? "",
            tuition: s.tuition ?? ""
        }));
        while (normalized.length < 4) {
            normalized.push({ ...EMPTY_SERVICE });
        }
        return normalized;
    };

    const getAgreementData = () => {
        if (!props.idToken || !props.s3Path) return;
        axios.get(`${process.env.REACT_APP_GATEWAY_URL}/agreements?s3_path=${props.s3Path}`, {
                headers: {
                    'Authorization': `Bearer ${props.idToken}`,
                    'Content-Type': 'application/json',
                },
            })
            .then(response => {
                setAgreementData({
                  ...response.data,
                  services: normalizeServices(response.data.services)
                });
            })
            .catch(error => {
                console.error('Error fetching data:', error);
            });
    };

    const extractPdf = () => {
        if (!props.idToken || !props.s3Path) return;
        axios.get(`${process.env.REACT_APP_GATEWAY_URL}/agreements/extraction?s3_path=${props.s3Path}`, {
                headers: {
                    'Authorization': `Bearer ${props.idToken}`,
                    'Content-Type': 'application/json',
                },
            })
            .then(response => {
                console.log("EXTRACTED");
            })
            .catch(error => {
                console.error('Error fetching data:', error);
            });
    }

    const handleChange = (e) => {
        const { name, value } = e.target;
        console.log(name, value);

        setAgreementData((prev) => ({
          ...prev,
          [name]: value,
        }));
    };

    const handleServiceChange = (index, field, value) => {
      setAgreementData(prev => {
        const services = [...(prev.services || [])];
        services[index] = {
          ...services[index],
          [field]: value,
        };
        return { ...prev, services };
      });
    };

    const handleSave = async (e) => {
        e.preventDefault();
        console.log("Saving:", agreementData);
        axios.put(`${process.env.REACT_APP_GATEWAY_URL}/agreements?s3_path=${props.s3Path}`,
            agreementData, 
            {
                headers: {
                    'Authorization': `Bearer ${props.idToken}`,
                    'Content-Type': 'application/json',
                },
            })
            .then((response) => {
                console.log(response.data);
            })
            .catch((error) => {
                console.error(error);
            });
    };

    return (
        <>
            {props.s3Path &&
            <>
                <form onSubmit={handleSave}>
                    <div style={{ display: "flex", alignItems: "center",
                            marginBottom: "8px"
                        }}
                    >
                        <label style={{ width: "25%", marginRight: "8px" }}>
                            Document type
                        </label>

                        <OverlayTrigger
                          placement="top"
                          overlay={<Tooltip id="tooltip-1">Document type</Tooltip>}
                        >
                            <input
                              type="text"
                              name={"document_title"}
                              value={agreementData.document_title}
                              onChange={handleChange}
                                style={{ width: "75%", marginRight: "5px" }}
                            />
                        </OverlayTrigger>
                    </div>

                    <div style={{ display: "flex", alignItems: "center",
                            marginBottom: "8px"
                        }}
                    >
                        <label style={{ width: "25%", marginRight: "8px" }}>
                            Student
                        </label>

                        <OverlayTrigger
                          placement="top"
                          overlay={<Tooltip id="tooltip-1">Student first name</Tooltip>}
                        >
                            <input
                              type="text"
                              name={"student_first_name"}
                              value={agreementData.student_first_name}
                              onChange={handleChange}
                              style={{ width: "25%", marginRight: "5px" }}
                            />
                        </OverlayTrigger>
                        <OverlayTrigger
                          placement="top"
                          overlay={<Tooltip id="tooltip-1">Student last name</Tooltip>}
                        >
                            <input
                              type="text"
                              name={"student_last_name"}
                              value={agreementData.student_last_name}
                              onChange={handleChange}
                              style={{ width: "25%", marginRight: "5px"  }}
                            />
                        </OverlayTrigger>
                        <OverlayTrigger
                          placement="top"
                          overlay={<Tooltip id="tooltip-1">Student nickname</Tooltip>}
                        >
                            <input
                              type="text"
                              name={"student_nickname"}
                              value={agreementData.student_nickname}
                              onChange={handleChange}
                                style={{ width: "25%", marginRight: "5px" }}
                            />
                        </OverlayTrigger>
                    </div>

                    <div style={{ display: "flex", alignItems: "center",
                            marginBottom: "8px"
                        }}
                    >
                        <label style={{ width: "25%", marginRight: "8px" }}>
                            Parent
                        </label>
                        <OverlayTrigger
                          placement="top"
                          overlay={<Tooltip id="tooltip-1">Parent full name</Tooltip>}
                        >
                            <input
                              type="text"
                              name={"parent_guardian_full_name"}
                              value={agreementData.parent_guardian_full_name}
                              onChange={handleChange}
                              style={{ width: "37.5%", marginRight: "10px" }} // input takes remaining space
                            />
                        </OverlayTrigger>
                        <OverlayTrigger
                          placement="top"
                          overlay={<Tooltip id="tooltip-1">Parent email</Tooltip>}
                        >
                            <input
                              type="text"
                              name={"parent_guardian_email"}
                              value={agreementData.parent_guardian_email}
                              onChange={handleChange}
                              style={{ width: "37.5%", marginRight: "5px" }}
                            />
                        </OverlayTrigger>
                    </div>

                    <div style={{ display: "flex", alignItems: "center",
                            marginBottom: "8px"
                        }}
                    >
                        <label style={{ width: "25%", marginRight: "8px" }}>
                            Second Parent
                        </label>
                        <OverlayTrigger
                          placement="top"
                          overlay={<Tooltip id="tooltip-1">Second parent fullname</Tooltip>}
                        >
                            <input
                              type="text"
                              name={"second_parent_guardian_full_name"}
                              value={agreementData.second_parent_guardian_full_name}
                              onChange={handleChange}
                              style={{ width: "37.5%", marginRight: "10px" }}
                            />
                        </OverlayTrigger>
                        <OverlayTrigger
                          placement="top"
                          overlay={<Tooltip id="tooltip-1">Second parent email</Tooltip>}
                        >
                            <input
                              type="text"
                              name={"second_parent_guardian_email"}
                              value={agreementData.second_parent_guardian_email}
                              onChange={handleChange}
                              style={{ width: "37.5%", marginRight: "5px" }}
                            />
                        </OverlayTrigger>
                    </div>

                    <div style={{ display: "flex", alignItems: "center",
                            marginBottom: "8px"
                        }}
                    >
                        <label style={{ width: "25%", marginRight: "5px" }}>
                            Campus / college bound / grade
                        </label>

                        <OverlayTrigger
                          placement="top"
                          overlay={<Tooltip id="tooltip-1">Student campus</Tooltip>}
                        >
                            <input
                              type="text"
                              name={"student_campus"}
                              value={agreementData.student_campus}
                              onChange={handleChange}
                              style={{ width: "35%", marginRight: "5px" }}
                            />
                        </OverlayTrigger>
                        <OverlayTrigger
                          placement="top"
                          overlay={<Tooltip id="tooltip-1">Student college bound</Tooltip>}
                        >
                            <input
                              type="text"
                              name={"student_college_bound"}
                              value={agreementData.student_college_bound}
                              onChange={handleChange}
                              style={{ width: "35%", marginRight: "5px"  }}
                            />
                        </OverlayTrigger>
                        <OverlayTrigger
                          placement="top"
                          overlay={<Tooltip id="tooltip-1">Student grade</Tooltip>}
                        >
                            <input
                              type="text"
                              name={"current_grade"}
                              value={agreementData.current_grade}
                              onChange={handleChange}
                              style={{ width: "5%", marginRight: "5px" }}
                            />
                        </OverlayTrigger>
                    </div>

                    <div style={{ display: "flex", alignItems: "center",
                            marginBottom: "8px"
                        }}
                    >
                        <label style={{ width: "15%", marginRight: "5px" }}>
                            Courses
                        </label>

                        <OverlayTrigger
                          placement="top"
                          overlay={<Tooltip>Courses</Tooltip>}
                        >
                            <textarea
                              type="text"
                              name={"student_courses"}
                              value={agreementData.student_courses}
                              onChange={handleChange}
                                style={{ width: "85%", height: "72px", marginRight: "5px" }}
                            />
                        </OverlayTrigger>
                    </div>

                    {agreementData.services.map((service, index) => (
                        <div key={index} style={{ display: "flex", alignItems: "center",
                                marginBottom: "8px"
                            }}
                        >
                            <OverlayTrigger
                              placement="top"
                              overlay={<Tooltip>Service {index+1} name</Tooltip>}
                            >
                                <input
                                  type="text"
                                  name={"service.service_name"}
                                  value={agreementData.services[index].service_name}
                                  onChange={(e) => handleServiceChange(index, "service_name", e.target.value)}
                                  style={{ width: "65%", marginRight: "5px" }}
                                />
                            </OverlayTrigger>

                            <OverlayTrigger
                              placement="top"
                              overlay={<Tooltip>Service {index+1} cost per unit</Tooltip>}
                            >
                                <input
                                  type="text"
                                  name={"service.cost_per_unit"}
                                  value={agreementData.services[index].cost_per_unit}
                                  onChange={(e) => handleServiceChange(index, "cost_per_unit", e.target.value)}
                                  style={{ width: "15%", marginRight: "5px" }}
                                />
                            </OverlayTrigger>

                            <OverlayTrigger
                              placement="top"
                              overlay={<Tooltip>Service {index+1} units</Tooltip>}
                            >
                                <input
                                  type="text"
                                  name={"service.units"}
                                  value={agreementData.services[index].units}
                                  onChange={(e) => handleServiceChange(index, "units", e.target.value)}
                                  style={{ width: "5%", marginRight: "5px" }}
                                />
                            </OverlayTrigger>

                            <OverlayTrigger
                              placement="top"
                              overlay={<Tooltip>Service {index+1} tuition</Tooltip>}
                            >
                                <input
                                  type="text"
                                  name={"service.tuition"}
                                  value={agreementData.services[index].tuition}
                                  onChange={(e) => handleServiceChange(index, "tuition", e.target.value)}
                                  style={{ width: "10%", marginRight: "5px" }}
                                />
                            </OverlayTrigger>
                        </div>
                    ))}

                    <div style={{ display: "flex", alignItems: "center",
                            marginBottom: "8px"
                        }}
                    >
                        <label style={{ width: "25%", marginRight: "8px" }}>
                            Sessions
                        </label>
                        <OverlayTrigger
                          placement="top"
                          overlay={<Tooltip>One to one sessions</Tooltip>}
                        >
                            <input
                              type="text"
                              name={"one_to_one_sessions"}
                              value={agreementData.one_to_one_sessions}
                              onChange={handleChange}
                              style={{ width: "10%", marginRight: "5px" }} // input takes remaining space
                            />
                        </OverlayTrigger>
                        <OverlayTrigger
                          placement="top"
                          overlay={<Tooltip id="tooltip-1">Homework studio sessions</Tooltip>}
                        >
                            <input
                              type="text"
                              name={"homework_studio_sessions"}
                              value={agreementData.homework_studio_sessions}
                              onChange={handleChange}
                                style={{ width: "10%", marginRight: "5px" }} // input takes remaining space
                            />
                        </OverlayTrigger>
                        <OverlayTrigger
                          placement="top"
                          overlay={<Tooltip id="tooltip-1">Total sessions purchased</Tooltip>}
                        >
                            <input
                              type="text"
                              name={"total_sessions_purchased"}
                              value={agreementData.total_sessions_purchased}
                              onChange={handleChange}
                                style={{ width: "10%", marginRight: "5px" }} // input takes remaining space
                            />
                        </OverlayTrigger>
                        <OverlayTrigger
                          placement="top"
                          overlay={<Tooltip id="tooltip-1">Total tuition</Tooltip>}
                        >
                            <input
                              type="text"
                              name={"total_tuition"}
                              value={agreementData.total_tuition}
                              onChange={handleChange}
                                style={{ width: "15%", marginRight: "5px" }} // input takes remaining space
                            />
                        </OverlayTrigger>

                        <OverlayTrigger
                          placement="top"
                          overlay={<Tooltip id="tooltip-1">Start date</Tooltip>}
                        >
                            <input
                              type="text"
                              name={"scheduled_start_date"}
                              value={agreementData.scheduled_start_date}
                              onChange={handleChange}
                              style={{ width: "25%" }}
                            />
                        </OverlayTrigger>
                    </div>

                    <div style={{ display: "flex", alignItems: "center",
                            marginBottom: "8px"
                        }}
                    >
                        <label style={{ width: "25%", marginRight: "8px" }}>
                            Payment
                        </label>

                        <OverlayTrigger
                          placement="top"
                          overlay={<Tooltip id="tooltip-1">Payment amount</Tooltip>}
                        >
                            <input
                              type="text"
                              name={"payment_amount"}
                              value={agreementData.payment_amount}
                              onChange={handleChange}
                              style={{ width: "35%" }}
                            />
                        </OverlayTrigger>

                        <OverlayTrigger
                          placement="top"
                          overlay={<Tooltip id="tooltip-1">Is single payment</Tooltip>}
                        >
                            <input
                              type="checkbox"
                              name={"is_single_payment"}
                              value={agreementData.is_single_payment}
                              // onChange={handleChange}
                                onChange={(e) =>
                                  handleChange({
                                    target: {
                                      name: "is_single_payment",
                                      value: e.target.checked
                                    }
                                  })
                                }
                              style={{ width: "35%" }}
                            />
                        </OverlayTrigger>
                    </div>

                    <div style={{ display: "flex", alignItems: "center",
                            marginBottom: "8px"
                        }}
                    >
                        <label style={{ width: "25%", marginRight: "8px" }}>
                            Document id
                        </label>

                        <OverlayTrigger
                          placement="top"
                          overlay={<Tooltip id="tooltip-1">Document id</Tooltip>}
                        >
                            <input
                              type="text"
                              name={"document_id"}
                              value={agreementData.document_id}
                              onChange={handleChange}
                              style={{ width: "75%", marginRight: "5px" }}
                            />
                        </OverlayTrigger>
                    </div>
                    <Button onClick={extractPdf} style={{ marginTop: "16px" }}>
                        Run extract data
                    </Button>

                    <Button type="submit" style={{ marginTop: "16px" }}>
                        Save
                    </Button>
                </form>
            </>
            }
        </>
    )
}

export default AgreementForm;
