import React from "react";
import { Link } from "react-router-dom"

const ImageBatch = ({ batch }) => (
    <li>
        <Link to={"/image_batch/" + batch.id}>{batch.id}: {batch.dirname}</Link>
    </li>
)

const VideoBatch = ({ batch }) => (
    <li>
        <Link to={"/video_batch/" + batch.id}>{batch.id}: {batch.dirname}</Link>
    </li>
)

const BatchOverview = ({ imageBatches, videoBatches }) => (
    <div className="batch-overview">
        <h1>Image Batches</h1>
        <ul className="batches">
            {imageBatches.map((batch) => (<ImageBatch key={batch.id} batch={batch} />))}
        </ul>
        <h1>Video Batches</h1>
        <ul className="batches">
            {videoBatches.map((batch) => (<VideoBatch key={batch.id} batch={batch} />))}
        </ul>
    </div>
)

export { BatchOverview };