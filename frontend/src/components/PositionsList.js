import React from "react";
import Position from "./Position";

export default function PositionsList({ positions }) {
    console.log(positions);
    return (
        <ul className="positions">
            {positions.map((position, i) => (
                console.log(position)
                // <Position key={i} {...position} />
            ))}
        </ul>
    );
}