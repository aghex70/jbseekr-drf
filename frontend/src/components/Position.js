import React from "react";

export default function Position({ name, role }) {
    return (
        <li>
            {role} {name}
        </li>
    );
}