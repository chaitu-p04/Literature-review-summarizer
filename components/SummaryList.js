import React from "react";
import { Card, Col, Row } from "react-bootstrap";

function SummaryList({ summaries }) {
    if (summaries.length === 0) {
        return (
            <p className="text-muted text-center">
                No summaries yet. Try searching a topic!
            </p>
        );
    }

    return (
        <Row className="mt-4">
            {summaries.map((paper, index) => (
                <Col md={6} lg={4} key={index} className="mb-4">
                    <Card className="shadow-sm h-100">
                        <Card.Body>
                            <Card.Title className="text-primary">{paper.title}</Card.Title>
                            <Card.Text style={{ whiteSpace: "pre-line" }}>
                                {paper.summary}
                            </Card.Text>
                        </Card.Body>
                    </Card>
                </Col>
            ))}
        </Row>
    );
}

export default SummaryList;
